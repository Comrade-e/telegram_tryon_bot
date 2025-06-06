from aiogram import types

keyboard_start = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Мои фото")],
        [types.KeyboardButton(text="Купить кредиты")],
        [types.KeyboardButton(text="Выбрать одежду для примерки")]
    ],
    resize_keyboard=True
)

keyboard_handle_generated_output = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [types.InlineKeyboardButton(text="Сохранить в папку", callback_data="save")]
    ],
    resize_keyboard=True
)

keyboard_menu_exit = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Вернуться в меню")]
    ],
    resize_keyboard=True)

def see_folders_to_choose_keyboard(folders: list):
    kb = []
    for folder in folders:
        kb.append([types.KeyboardButton(text=folder)])
    kb.append([types.KeyboardButton(text="Назад")])
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb)
    return keyboard



def see_folders_keyboard(folders: list):
    kb = []
    for folder in folders:
        kb.append([types.KeyboardButton(text=folder)])
    kb.append([types.KeyboardButton(text="Создать новую папку")])
    kb.append([types.KeyboardButton(text="Назад")])
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb)
    return keyboard

def create_folders_keyboard():
    kb = []
    kb.append([types.KeyboardButton(text="Создать новую папку")])
    kb.append([types.KeyboardButton(text="Назад")])
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb)
    return keyboard


def create_folder_actions_keyboard(folder_name: str):
    kb = []
    kb.append([types.KeyboardButton(text=f"Показать все фото в '{folder_name}'")])
    kb.append([types.KeyboardButton(text=f"Загрузить фото в '{folder_name}'")])
    kb.append([types.KeyboardButton(text="Назад к папкам")])
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb)
    return keyboard

