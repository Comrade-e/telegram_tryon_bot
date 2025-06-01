from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def form_markup_with_callback_data(f: str, callback_header: str):
    button = InlineKeyboardButton(text="✅", callback_data=callback_header + f)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return keyboard