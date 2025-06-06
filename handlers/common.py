import logging

import aiogram

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from ai_generation_contraptions import *
from file_opening_contraptions import *
from handlers.choosing_state_changer import register_choosing_stage_changer
from hashing import get_user_hash, get_photo_hash
from aiogram.filters import Command

from keyboards.common import *
from keyboards.choose_confirms import *

from aiogram.fsm.state import State, StatesGroup
from aiogram import types
from aiogram.fsm.context import FSMContext

image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')

BASE_STATE = State()


class PhotoFolders(StatesGroup):
    choosing_folder = State()
    folder_actions = State()
    waiting_for_photo = State()
    creating_folder = State()


class ChoosingStates(StatesGroup):
    choosing_model = State()
    choosing_top = State()
    choosing_bottom = State()
    pre_confirm = State()
    final_confirm = State()


class GenerationStates(StatesGroup):
    on_generation = State()
    exit_generation = State()


def pass_dispatcher(dp: aiogram.Dispatcher):
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message, state: FSMContext):
        await message.answer(
            "<текст приветствия>",
            reply_markup=keyboard_start
        )
        await state.set_state(BASE_STATE)

    @dp.message(BASE_STATE)
    async def folder_interaction(msg: types.Message, state: FSMContext):
        if msg.text in ("Мои фото", 'Выбрать одежду для примерки'):
            user_hash = get_user_hash(msg.from_user.id)
            user_dir = f'user_photos/{user_hash}'
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)
            folders = [d for d in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, d))]
            if folders:
                await msg.answer("Выберите папку:" if msg.text == "Мои фото" else "Выберите фото модели из папок",
                                 reply_markup=see_folders_keyboard(folders) if msg.text == "Мои фото"
                                 else see_folders_to_choose_keyboard(folders))
                await state.set_state(
                    PhotoFolders.choosing_folder if msg.text == "Мои фото" else ChoosingStates.choosing_model)

            else:
                await msg.answer("У вас пока нету папок!", reply_markup=create_folders_keyboard())
                await state.set_state(PhotoFolders.choosing_folder)

    @dp.message(PhotoFolders.choosing_folder)
    async def handle_folder_choice(msg: types.Message, state: FSMContext):
        user_hash = get_user_hash(msg.from_user.id)
        user_dir = f'user_photos/{user_hash}'
        folders = [d for d in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, d))]
        if msg.text in folders:
            await state.set_state(PhotoFolders.folder_actions)
            await state.update_data(selected_folder=msg.text)
            await msg.answer(f'Папка "{msg.text}". Выберите действие',
                             reply_markup=create_folder_actions_keyboard(msg.text))
            # folder_path = os.path.join(user_dir, msg.text)
            # files = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
            # for f in files:
            # await msg.answer_photo(FSInputFile(os.path.join(folder_path, f)))
        else:
            if (msg.text == "Создать новую папку") and (await state.get_state() == PhotoFolders.choosing_folder.state):
                await msg.answer("Введите название новой папки:")
                await state.set_state(PhotoFolders.creating_folder)
                return
            elif msg.text == "Назад":
                await msg.answer("Главное меню:", reply_markup=keyboard_start)
                await state.set_state(BASE_STATE)
            else:
                await msg.answer("Папка не найдена. Пожалуйста, выберите из списка.",
                                 reply_markup=see_folders_keyboard(folders))
            return

    @dp.message(PhotoFolders.creating_folder)
    async def create_new_folder(msg: types.Message, state: FSMContext):
        user_hash = get_user_hash(msg.from_user.id)
        user_dir = f'user_photos/{user_hash}'
        if msg.text == "Назад":
            await state.set_state(PhotoFolders.choosing_folder)
            await msg.answer("Главное меню", reply_markup=see_folders_keyboard(get_folders(user_dir)))
        else:
            new_folder = msg.text.strip()
            if not new_folder or any(c in new_folder for c in '/\\') or len(new_folder) > 16:
                await msg.answer("Недопустимое или слишком длинное имя папки. Попробуйте другое.")
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
                    await msg.answer_photo(FSInputFile(os.path.join(folder_path, file)))
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
            await msg.answer("Пожалуйста, выберите действие с помощью кнопок",
                             reply_markup=create_folder_actions_keyboard(folder))

    @dp.message(PhotoFolders.waiting_for_photo)
    async def handle_photo_upload(msg: types.Message, state: FSMContext):
        data = await state.get_data()
        folder = data.get('selected_folder')
        user_hash = get_user_hash(msg.from_user.id)
        user_dir = os.path.join('user_photos', user_hash)
        folder_path = os.path.join(user_dir, folder)

        if not msg.photo:
            await msg.answer("Пожалуйста, отправьте изображение.")
            return
        await save_photo(msg, folder_path)

        # Обновление состояния
        await msg.answer(f"Папка '{folder}'. Выберите действие:",
                         reply_markup=create_folder_actions_keyboard(folder))
        await state.set_state(PhotoFolders.folder_actions)

    @dp.message(ChoosingStates.pre_confirm)
    async def pre_generation_check(msg: types.Message, state: FSMContext):
        data = await state.get_data()
        model = data.get("model")
        top = data.get("top")
        bottom = data.get("bottom")
        group = create_photo_media_group([model, top, bottom], ["Модель", "Верх", "Низ"])
        await msg.bot.send_media_group(
            chat_id=msg.chat.id,
            media=group)
        await state.set_state(ChoosingStates.final_confirm)
        await msg.answer("Отправить на генерацию", reply_markup=final_keyboard)

    @dp.message(ChoosingStates.final_confirm)
    async def send_for_generation(msg: types.Message, state: FSMContext):
        if msg.text == "Отмена":
            await msg.answer("Главное меню:", reply_markup=keyboard_start)
            await state.set_state(BASE_STATE)
        elif msg.text == "Сгенерировать":
            data = await state.get_data()
            model = data.get("chosen_model")
            top = data.get("chosen_top")
            bottom = data.get("chosen_bottom")
            await msg.answer("Фото отправлено на генерацию")
            await state.set_state(GenerationStates.on_generation)
            await handle_generation(msg, *(model, top, bottom))
            await state.set_state(GenerationStates.exit_generation)

    @dp.message(GenerationStates.on_generation)
    async def freeze_interaction_on_generation(msg: types.Message):
        await msg.answer("Генерация...")

    @dp.message(GenerationStates.exit_generation)
    async def exit_generation(msg: types.Message, state: FSMContext):
        if msg.text == "Вернуться в меню":
            await msg.reply("Меню", reply_markup=keyboard_start)
            await state.set_state(BASE_STATE)

    @dp.callback_query(GenerationStates.exit_generation)
    async def save_generated(callback_query: CallbackQuery, state: FSMContext):
        if callback_query.data == "save":
            folder = "Сгенерированные"
            user_hash = get_user_hash(callback_query.from_user.id)
            user_dir = os.path.join('user_photos', user_hash)
            folder_path = os.path.join(user_dir, folder)
            await save_photo(callback_query.message, folder_path)
            await callback_query.answer("Фото сохранено")
            await callback_query.message.answer("Меню", reply_markup=keyboard_start)
            await state.set_state(BASE_STATE)

    register_choosing_stage_changer(dp, ChoosingStates.choosing_model, "model",
                                    "Фото модели выбрано. Выберите фото верхней одежды", ChoosingStates.choosing_top)

    register_choosing_stage_changer(dp, ChoosingStates.choosing_top, "top",
                                    "Фото верхней одежды выбрано. Выберите фото нижней одежды",
                                    ChoosingStates.choosing_bottom)

    register_choosing_stage_changer(dp, ChoosingStates.choosing_bottom, "bottom",
                                    "Фото нижней одежды выбрано. Нажмите, чтобы подтвердить",
                                    ChoosingStates.pre_confirm,
                                    use_final_keyboard=True)

    return dp
