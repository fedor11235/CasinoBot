# Импортируем нужные библиотеки
import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from db.models import init_db
from aiogram.enums import ParseMode

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Получаем токен бота
BOT_TOKEN = "7949770451:AAGcWxCGApTKBX939JuMRV8bDyjF70gqWoI"

async def main():
    try:
        # Инициализируем базу данных
        await init_db()
        
        # Создаем хранилище состояний
        storage = MemoryStorage()
        
        # Инициализируем бота и диспетчер
        bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
        dp = Dispatcher(storage=storage)
        
        # Импортируем роутеры
        from handlers.states import router as states_router
        from handlers.start import router as start_router
        from handlers.games import router as games_router
        from handlers.balance import router as balance_router
        from handlers.extra import router as extra_router
        from handlers import travel, routes, guides, support
        
        # Регистрируем все обработчики
        dp.include_router(states_router)  # Сначала регистрируем states
        dp.include_router(start_router)
        dp.include_router(games_router)
        dp.include_router(balance_router)
        dp.include_router(extra_router)
        dp.include_router(travel.router)
        dp.include_router(routes.router)
        dp.include_router(guides.router)
        dp.include_router(support.router)
        
        # Запускаем бота
        logger.info("Starting bot...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)