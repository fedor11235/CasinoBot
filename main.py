# Импортируем нужные библиотеки
import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from keyboards.inline import get_main_menu_keyboard, get_profile_keyboard, get_rules_keyboard
from db.database import get_or_create_user, update_user_stats

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():
    try:
        storage = MemoryStorage()
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher(storage=storage)
        
        # Обработчик команды /start
        @dp.message(Command("start"))
        async def cmd_start(message: types.Message):
            user = get_or_create_user(message.from_user.id, message.from_user.username)
            await message.answer(
                f"👋 Привет, {message.from_user.first_name}!\n"
                "Добро пожаловать в Казино Бот!\n"
                "Выберите действие в меню ниже:",
                reply_markup=get_main_menu_keyboard()
            )
        
        # Обработчик кнопки профиля
        @dp.callback_query(lambda c: c.data == "profile")
        async def show_profile(callback: types.CallbackQuery):
            user = get_or_create_user(callback.from_user.id, callback.from_user.username)
            await callback.message.edit_text(
                f"👤 Профиль игрока\n\n"
                f"Имя: {callback.from_user.first_name}\n"
                f"Побед: {user.total_wins}\n"
                f"Всего звёзд: {user.total_stars:.2f} ⭐️\n\n"
                f"Для пополнения баланса нажмите кнопку 'Внести оплату'\n"
                f"По всем вопросам обращайтесь в обратную связь",
                reply_markup=get_profile_keyboard()
            )
        
        # Обработчик кнопки правил
        @dp.callback_query(lambda c: c.data == "rules")
        async def show_rules(callback: types.CallbackQuery):
            rules_text = (
                "📖 Правила игры:\n\n"
                "1. Игра ведётся на звёзды ⭐️\n"
                "2. Вы делаете ставку и бросаете кости\n"
                "3. Если сумма на костях больше 7 - вы выигрываете\n"
                "4. Если сумма меньше или равна 7 - вы проигрываете\n"
                "5. При выигрыше вы получаете удвоенную ставку\n"
                "6. При проигрыше теряете ставку\n\n"
                "Удачи в игре! 🎲"
            )
            await callback.message.edit_text(rules_text, reply_markup=get_rules_keyboard())
        
        # Обработчик возврата в главное меню
        @dp.callback_query(lambda c: c.data == "main_menu")
        async def return_to_menu(callback: types.CallbackQuery):
            await callback.message.edit_text(
                "Главное меню\nВыберите действие:",
                reply_markup=get_main_menu_keyboard()
            )
        
        # Обработчик кнопки оплаты
        @dp.callback_query(lambda c: c.data == "payment")
        async def show_payment(callback: types.CallbackQuery):
            await callback.message.edit_text(
                "💳 Для пополнения баланса свяжитесь с администратором:\n"
                "@monomomn\n\n"
                "Укажите сумму пополнения и ваш ID в боте.",
                reply_markup=get_profile_keyboard()
            )
        
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