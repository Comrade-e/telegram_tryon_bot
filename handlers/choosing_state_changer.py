import os

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery

from handlers.common import ChoosingStates, image_extensions
from hashing import get_user_hash
from keyboards.common import keyboard_start, see_folders_to_choose_keyboard, see_folders_keyboard
from keyboards.choose_confirms import *


def register_choosing_stage_changer(dp: Dispatcher, trigger_state: State, state_data_key: str, message_when_confirm: str,
                                    next_state: State):
    @dp.message(trigger_state)
    async def universal_handler(callback_query: CallbackQuery, state: FSMContext):
        msg = callback_query.message
        user_hash = get_user_hash(msg.from_user.id)
        user_dir = f'user_photos/{user_hash}'
        folders = [d for d in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, d))]
        if msg.text == "Назад":
            await msg.answer("Главное меню:", reply_markup=keyboard_start)
            await state.clear()
            return
        if msg.text in folders:
            await state.update_data(selected_folder=msg.text)
            folder_path = os.path.join(user_dir, msg.text)
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
            for f in files:
                await msg.answer_photo(photo=os.path.join(folder_path, f), reply_markup=
                form_markup_with_callback_data(f, state_data_key))
        else:
            await msg.answer("Папка не найдена. Пожалуйста, выберите из списка.",
                             reply_markup=see_folders_to_choose_keyboard(folders))

    @dp.callback_query(lambda c: c.startswith(state_data_key))
    async def commit_choice(callback_query: CallbackQuery, state: FSMContext):
        await state.update_data(**{state_data_key: callback_query.data.split(':')[-1]})
        await state.set_state(next_state)
        user_hash = get_user_hash(callback_query.message.from_user.id)
        user_dir = f'user_photos/{user_hash}'
        folders = [d for d in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, d))]
        await callback_query.message.answer(message_when_confirm, reply_markup=see_folders_to_choose_keyboard(folders))


