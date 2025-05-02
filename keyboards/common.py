from aiogram import types

keyboard_start = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Загрузить пользовательское фото модели")],
        [types.KeyboardButton(text="Выбрать манекен")],
        [types.KeyboardButton(text="Загрузить фото одежды")],
        [types.KeyboardButton(text="Купить кредиты")],
        [types.KeyboardButton(text="Генерировать")]
    ],
    resize_keyboard=True
)


def create_confirm_mannequin_for_filename(filename):
    keyboard_confirm_mannequin = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='✔', callback_data=f'mannequin_confirm:{filename}')]
    ])
    return keyboard_confirm_mannequin
