import os

from aiogram import types
from aiogram.fsm.state import State

from hashing import get_user_hash, get_photo_hash
from aiogram.fsm.context import FSMContext



class PhotoLoadingHandlerTemplater:
    def __init__(self, button_message: str, directory_name: str, state_to_set: State, state_to_check: State):
        self.state_to_check = state_to_check
        self.state_to_set = state_to_set
        self.button_message = button_message
        self.directory_name = directory_name



    def _create_photo_waiter(self, dp):
        @dp.message(lambda msg: msg.text == self.button_message)
        async def waiter(msg: types.Message, state: FSMContext):
            await state.set_state(self.state_to_set)
            await msg.answer('Загрузите одно фото и отправьте в чат')

    def _create_photo_downloader(self, dp):
        @dp.message(self.state_to_check)
        async def downloader(msg: types.Message, state: FSMContext):


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
            finally:
                await state.clear()

    def create_all(self, dp):
        self._create_photo_waiter(dp)
        self._create_photo_downloader(dp)
