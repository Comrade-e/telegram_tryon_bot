import aiogram
from aiogram import types
from aiogram.filters import Command

from keyboards.common import *
from user_mannequin_choises import UserChoicesDict

def pass_dispatcher(dp: aiogram.Dispatcher):
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer(
            "<текст приветствия>",
            reply_markup=keyboard_start
        )

    @dp.message(lambda msg: msg.text == "Выбрать манекен")
    async def select_mannequin(msg: types.Message):
        for path in ['male1', 'male2', 'female1', 'female2']:
            photo = types.FSInputFile(f'example_photos/{path}.jpg')
            await msg.answer_photo(photo=photo, reply_markup=create_confirm_mannequin_for_filename(path))



    @dp.callback_query(lambda q: q.data.startswith('mannequin_confirm'))
    async def confirm_mannequin(callback_query: types.CallbackQuery):
        res = callback_query.data.split(':')[-1]
        print(res)
        UserChoicesDict().DICT[callback_query.from_user.id] = res
        await callback_query.answer()


    return dp
