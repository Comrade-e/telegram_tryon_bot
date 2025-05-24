import aiogram
import os

from hashing import get_user_hash, get_photo_hash
from aiogram.filters import Command

from keyboards.common import *
from user_mannequin_choises import UserChoicesDict
from handlers.photo_loading_template import PhotoLoadingHandlerTemplater

from aiogram.fsm.state import State, StatesGroup


image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')


class PhotoWaitingStates(StatesGroup):
    wait_for_model = State()
    wait_for_top = State()
    wait_for_bottom = State()



def pass_dispatcher(dp: aiogram.Dispatcher):

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer(
            "<текст приветствия>",
            reply_markup=keyboard_start
        )

    @dp.message(lambda msg: msg.text == "Выбрать манекен")
    async def select_mannequin(msg: types.Message):
        user_hash = get_user_hash(msg.from_user.id)
        if os.path.exists(f'user_photos/{user_hash}/models'):
            for root, dirs, files in os.walk(f'user_photos/{user_hash}/models'):
                for filename in files:
                    if filename.lower().endswith(image_extensions):
                        photo_path = os.path.join(root, filename)
                        photo = types.FSInputFile(photo_path)
                        await msg.answer_photo(photo=photo,
                                               reply_markup=create_confirm_mannequin_for_filename(filename))

        for filename in ['male1.jpg', 'male2.jpg', 'female1.jpg', 'female2.jpg']:
            photo = types.FSInputFile(f'example_photos/{filename}')
            await msg.answer_photo(photo=photo, reply_markup=create_confirm_mannequin_for_filename(filename))



    @dp.callback_query(lambda q: q.data.startswith('mannequin_confirm'))
    async def confirm_mannequin(callback_query: types.CallbackQuery):
        res = callback_query.data.split(':')[-1]
        #print(res)
        user_hash = get_user_hash(callback_query.from_user.id)
        UserChoicesDict().DICT[user_hash] = res
        await callback_query.answer()
        await callback_query.message.answer(f'Фото выбрано.')

    PhotoLoadingHandlerTemplater('Загрузить пользовательское фото модели', 'models',
                                 PhotoWaitingStates.wait_for_model, PhotoWaitingStates.wait_for_model).create_all(dp)

    PhotoLoadingHandlerTemplater('Загрузить фото нижней одежды', 'top_garments',
                                 PhotoWaitingStates.wait_for_top, PhotoWaitingStates.wait_for_top).create_all(dp)

    PhotoLoadingHandlerTemplater('Загрузить фото верхней одежды', 'bottom_garments',
                                 PhotoWaitingStates.wait_for_bottom, PhotoWaitingStates.wait_for_bottom).create_all(dp)














    return dp
