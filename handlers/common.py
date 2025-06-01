import logging

import aiogram
import os

from aiogram.exceptions import TelegramBadRequest

from hashing import get_user_hash, get_photo_hash
from aiogram.filters import Command, StateFilter

from keyboards.common import *
from keyboards.choose_confirms import *

from aiogram.fsm.state import State, StatesGroup
from aiogram import types
from aiogram.fsm.context import FSMContext

image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')


class PhotoFolders(StatesGroup):
    choosing_folder = State()
    folder_actions = State()
    waiting_for_photo = State()
    creating_folder = State()


class ChoosingStates(StatesGroup):
    choosing_model = State()
    choosing_top = State()
    choosing_bottom = State()


def pass_dispatcher(dp: aiogram.Dispatcher):
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer(
            "<текст приветствия>",
            reply_markup=keyboard_start
        )

    @dp.message(lambda msg: msg.text in ("Мои фото", 'Выбрать одежду для примерки'))
    async def folder_interaction(msg: types.Message, state: FSMContext):
        user_hash = get_user_hash(msg.from_user.id)
        user_dir = f'user_photos/{user_hash}'
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        folders = [d for d in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, d))]
        if folders:
            await msg.answer("Выберите фото модели:",
                             reply_markup=see_folders_keyboard(folders) if msg.text == "Мои фото"
                             else see_folders_to_choose_keyboard(folders))
            await state.set_state(
                PhotoFolders.choosing_folder if msg.text == "Мои фото" else ChoosingStates.choosing_model)

        else:
            await msg.answer("У вас пока нету папок!", reply_markup=create_folders_keyboard())
            await state.set_state(PhotoFolders.choosing_folder)

    @dp.message(state=StateFilter(PhotoFolders.choosing_folder))
    async def handle_folder_choice(msg: types.Message, state: FSMContext):
        user_hash = get_user_hash(msg.from_user.id)
        user_dir = f'user_photos/{user_hash}'
        folders = [d for d in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, d))]
        if (msg.text == "Создать новую папку") and (state == PhotoFolders.choosing_folder):
            await msg.answer("Введите название новой папки:")
            await state.set_state(PhotoFolders.creating_folder)
            return
        if msg.text == "Назад":
            await msg.answer("Главное меню:", reply_markup=keyboard_start)
            await state.clear()
            return
        if msg.text in folders:
            await state.update_data(selected_folder=msg.text)
            folder_path = os.path.join(user_dir, msg.text)
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
            for f in files:
                await msg.answer_photo(photo=os.path.join(folder_path, f))
        else:
            await msg.answer("Папка не найдена. Пожалуйста, выберите из списка.",
                             reply_markup=see_folders_keyboard(folders))

    @dp.message(PhotoFolders.creating_folder)
    async def create_new_folder(msg: types.Message, state: FSMContext):
        user_hash = get_user_hash(msg.from_user.id)
        user_dir = f'user_photos/{user_hash}'
        new_folder = msg.text.strip()
        if not new_folder or any(c in new_folder for c in '/\\'):
            await msg.answer("Недопустимое имя папки. Попробуйте другое.")
            return
        new_folder_path = os.path.join(user_dir, new_folder)
        if os.path.exists(new_folder_path):
            await msg.answer("Папка с таким именем уже существует.")
            return
        os.makedirs(new_folder_path)
        folders = [d for d in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, d))]
        await msg.answer("Папка создана! Выберите папку:", reply_markup=see_folders_keyboard(folders))
        await state.set_state(PhotoFolders.choosing_folder)

    @dp.message(PhotoFolders.folder_actions)
    async def handle_folder_actions(msg: types.Message, state: FSMContext):
        data = await state.get_data()
        folder = data.get('selected_folder')
        user_hash = get_user_hash(msg.from_user.id)
        user_dir = f'user_photos/{user_hash}'
        folder_path = os.path.join(user_dir, folder)
        if msg.text == f"Показать все фото в '{folder}'":
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
            if not files:
                await msg.answer("В папке нет фотографий.")
            else:
                for file in files:
                    await msg.answer_photo(photo=os.path.join(folder_path, file))
            await msg.answer(f"Папка '{folder}'. Выберите действие:",
                             reply_markup=create_folder_actions_keyboard(folder))
        elif msg.text == f"Загрузить фото в '{folder}'":
            await msg.answer("Отправьте фото для загрузки в эту папку.")
            await state.set_state(PhotoFolders.waiting_for_photo)
        elif msg.text == "Назад к папкам":
            folders = [d for d in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, d))]
            await msg.answer("Выберите папку:", reply_markup=see_folders_keyboard(folders))
            await state.set_state(PhotoFolders.choosing_folder)
        else:
            await msg.answer("Пожалуйста, выберите действие с помощью кнопок.",
                             reply_markup=create_folder_actions_keyboard(folder))

    @dp.message(PhotoFolders.waiting_for_photo)
    async def handle_photo_upload(msg: types.Message, state: FSMContext):
        data = await state.get_data()
        folder = data.get('selected_folder')
        user_hash = get_user_hash(msg.from_user.id)
        user_dir = os.path.join('user_photos', user_hash)
        folder_path = os.path.join(user_dir, folder)

        # Создаём все необходимые директории
        os.makedirs(folder_path, exist_ok=True)  # Критически важная строка!

        if not msg.photo:
            await msg.answer("Пожалуйста, отправьте изображение.")
            return

        try:
            # Берём фото максимального качества
            photo = msg.photo[-1]

            # Получаем информацию о файле
            file = await msg.bot.get_file(photo.file_id)
            # Добавьте отладочный вывод
            print(f"File ID: {photo.file_id}")
            print(f"File unique ID: {photo.file_unique_id}")  # Для долгосрочного хранения
            print(file.file_path)

            # Проверяем полученный file_path
            if not file.file_path:
                await msg.answer("Ошибка: неверный идентификатор файла.")
                return

            # Проверяем расширение файла
            ext = os.path.splitext(file.file_path)[1].lower()
            if ext not in {'.jpg', '.jpeg', '.png'}:  # Явное указание разрешённых расширений
                await msg.answer("Разрешены только JPG/PNG изображения.")
                return

            # Генерируем уникальное имя файла
            file_name = f"{get_photo_hash(str(photo.file_id))}{ext}"
            dest = os.path.join(folder_path, file_name)

            # Скачивание с обработкой ошибок
            try:
                await msg.bot.download_file(file.file_path, destination=dest)
            except TelegramBadRequest as e:
                await msg.answer(f"Ошибка Telegram: {e.message}")
                return
            except Exception as e:
                await msg.answer(f"Ошибка скачивания: {str(e)}")
                return

            await msg.answer("✅ Фото успешно загружено!")

        except Exception as e:
            logging.error(f"Critical error: {str(e)}")
            await msg.answer("⚠️ Произошла внутренняя ошибка. Попробуйте ещё раз.")

        # Обновление состояния
        await msg.answer(f"Папка '{folder}'. Выберите действие:",
                         reply_markup=create_folder_actions_keyboard(folder))
        await state.set_state(PhotoFolders.folder_actions)

    return dp
