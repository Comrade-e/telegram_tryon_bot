import asyncio

from aiogram import types
from aiogram.types import FSInputFile

from keyboards.common import *


async def handle_generation(msg: types.Message, *file_paths):
    # Здесь должно быть взаиодействие с API
    await asyncio.sleep(4)  # "генерация"
    await msg.answer_photo(FSInputFile("dummy.png"), reply_markup=keyboard_handle_generated_output)
    await msg.answer("Выберите действие", reply_markup=keyboard_menu_exit)


