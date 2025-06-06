import os

from aiogram import Dispatcher
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery

from file_opening_contraptions import get_folders
from hashing import get_user_hash
from keyboards.common import keyboard_start, see_folders_to_choose_keyboard
from keyboards.choose_confirms import *

from pathlib import Path
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext


def register_choosing_stage_changer(dp: Dispatcher, trigger_state: State, state_data_key: str, message_when_confirm: str,
                                    next_state: State, use_final_keyboard=False):
    @dp.message(trigger_state)
    async def universal_handler(msg: Message, state: FSMContext):
        user_hash = get_user_hash(msg.from_user.id)
        user_dir = Path('user_photos') / user_hash

        if not user_dir.exists():
            await msg.answer("Ошибка: ваша папка не найдена")
            return

        # Получаем список папок
        folders = get_folders(user_dir)

        if msg.text == "Назад":
            await msg.answer("Главное меню:", reply_markup=keyboard_start)
            await state.clear()
            return

        if msg.text in folders:
            await state.update_data(selected_folder=msg.text)
            folder_path = user_dir / msg.text

            # Получаем список файлов изображений
            image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
            files = [f for f in folder_path.iterdir() if f.suffix.lower() in image_extensions]

            for file_path in files:
                # Формируем относительный путь для callback
                relative_path = file_path.relative_to('user_photos')

                # Создаем клавиатуру с callback_data содержащей путь файла
                keyboard = form_markup_with_callback_data(relative_path, state_data_key)
                await msg.answer_photo(
                    photo=FSInputFile(file_path),
                    reply_markup=keyboard
                )


    @dp.callback_query(lambda c: c.data.startswith(state_data_key))
    async def commit_choice(callback_query: CallbackQuery, state: FSMContext):
        await state.update_data(**{state_data_key: callback_query.data.split(':')[-1]})
        await state.set_state(next_state)
        user_hash = get_user_hash(callback_query.from_user.id)
        user_dir = f'user_photos/{user_hash}'
        folders = get_folders(user_dir)
        await callback_query.message.answer(message_when_confirm, reply_markup=keyboard_final_commit if
        use_final_keyboard else see_folders_to_choose_keyboard(folders))
        await callback_query.answer()
