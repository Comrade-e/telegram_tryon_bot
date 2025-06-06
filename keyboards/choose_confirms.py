
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def form_markup_with_callback_data(f: str, callback_header: str):
    button = InlineKeyboardButton(text="✅", callback_data=f"{callback_header}:{f}")
    print(f"{callback_header}:{f}")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return keyboard

keyboard_final_commit = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Просмотреть фото и подтвердить")]
    ],
    resize_keyboard=True)

final_keyboard =  ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сгенерировать", callback_data="accept")],
        [KeyboardButton(text="Отмена", callback_data="discard")]
    ],
    resize_keyboard=True)