import asyncio
import logging
from aiogram import Bot, Dispatcher, types

from handlers.common import pass_dispatcher
from user_mannequin_choises import UserChoicesDict

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="7910484171:AAEC-mZQC5_UVW1e7w6JdKHe0tdUCO7HIsA")
# Диспетчер
dp = Dispatcher()

dp = pass_dispatcher(dp)

# Запуск процесса поллинга новых апдейтов
async def main():
    UserChoicesDict()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
