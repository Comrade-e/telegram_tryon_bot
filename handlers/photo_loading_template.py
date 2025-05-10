import os

from aiogram import types
from common import get_user_hash, get_photo_hash


class PhotoLoadingHandlerTemplater:
    def __init__(self, button_message: str, directory_name: str):
        self.button_message = button_message
        self.directory_name = directory_name
        self.is_waiting = dict()

    def create_photo_waiter(self, dp):
        @dp.message(lambda msg: msg.text == self.button_message)
        async def waiter(msg: types.Message):
            self.is_waiting[get_user_hash(msg.from_user.id)] = True
            await msg.answer('Загрузите одно фото и отправьте в чат')

    def create_photo_downloader(self, dp):
        @dp.message(lambda msg: self.is_waiting[get_user_hash(msg.from_user.id)])
        async def downloader(msg: types.Message):

            self.is_waiting[get_user_hash(msg.from_user.id)] = True

            if not os.path.exists('user_photos'):
                os.makedirs('user_photos')
            user_hash = get_user_hash(msg.from_user.id)
            user_dir_path = os.path.join('user_photos', os.path.join(user_hash, self.directory_name))

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
                await msg.reply(f'Загрузите одно фото')