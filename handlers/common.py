import hashlib

import aiogram
import os
import hmac
from hashkey import HASH_KEY
from aiogram.filters import Command

from keyboards.common import *
from user_mannequin_choises import UserChoicesDict


image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')

def get_user_hash(userid: int):
    return hmac.new(HASH_KEY, str(userid).encode('utf-8'), hashlib.sha256).hexdigest()

def get_photo_hash(photo_name: str):
    return hmac.new(HASH_KEY, photo_name.encode('utf-8'), digestmod=lambda: hashlib.blake2b(digest_size=8)).hexdigest()

def pass_dispatcher(dp: aiogram.Dispatcher):

    global WAIT_FOR_MODEL_PHOTO
    WAIT_FOR_MODEL_PHOTO = False

    global WAIT_FOR_CLOTHING_PHOTO
    WAIT_FOR_CLOTHING_PHOTO = False

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

    @dp.message(lambda msg: msg.text == 'Загрузить пользовательское фото модели')
    async def ready_for_photo(msg: types.Message):
        global WAIT_FOR_MODEL_PHOTO
        WAIT_FOR_MODEL_PHOTO = True
        await msg.answer('Загрузите одно фото и отправьте в чат')

    @dp.message(lambda msg: WAIT_FOR_MODEL_PHOTO)
    async def load_custom_photo(msg: types.Message):
        global WAIT_FOR_MODEL_PHOTO
        WAIT_FOR_MODEL_PHOTO = False

        if not os.path.exists('user_photos'):
            os.makedirs('user_photos')
        user_hash = get_user_hash(msg.from_user.id)
        user_dir_path = os.path.join('user_photos', os.path.join(user_hash, 'models'))

        if not os.path.exists(user_dir_path):
            os.makedirs(user_dir_path)

        try:
            bot = msg.bot
            photo = msg.photo[-1]
            file_id = photo.file_id
            file_obj = await bot.get_file(file_id)
            file_path = file_obj.file_path
            await bot.download_file(file_path, os.path.join(user_dir_path,
                                                            f'{get_photo_hash(file_id)}.jpg'))


            await msg.reply('Фото загружено')
        except TypeError:
            await msg.reply(f'Загрузите фото')

    @dp.message(lambda msg: msg.text == 'Загрузить фото одежды')
    async def ready_for_clothing_photo(msg: types.Message):
        global WAIT_FOR_CLOTHING_PHOTO
        WAIT_FOR_CLOTHING_PHOTO = True
        await msg.answer('Загрузите одно фото и отправьте в чат')

    @dp.message(lambda msg: WAIT_FOR_CLOTHING_PHOTO)
    async def load_custom_clothing_photo(msg: types.Message):
        global WAIT_FOR_CLOTHING_PHOTO
        WAIT_FOR_CLOTHING_PHOTO = False
        if not os.path.exists('user_photos'):
            os.makedirs('user_photos')
        user_hash = get_user_hash(msg.from_user.id)
        user_dir_path = os.path.join('user_photos', os.path.join(user_hash, 'clothes'))

        if not os.path.exists(user_dir_path):
            os.makedirs(user_dir_path)

        try:
            bot = msg.bot
            photo = msg.photo[-1]
            file_id = photo.file_id
            file_obj = await bot.get_file(file_id)
            file_path = file_obj.file_path
            await bot.download_file(file_path, os.path.join(user_dir_path,
                                                            f'{get_photo_hash(file_id)}.jpg'))


            await msg.reply('Фото загружено')
        except TypeError:
            await msg.reply(f'Загрузите фото')









    return dp
