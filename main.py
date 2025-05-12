# Импортируем нужные библиотеки
import os
import asyncio
import logging
import random
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from keyboards.inline import get_main_menu_keyboard, get_profile_keyboard, get_rules_keyboard
from db.database import get_or_create_user, update_user_stats, add_stars_to_user

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

class GameStates(StatesGroup):
    waiting_for_bet = State()

async def safe_edit_message(message: types.Message, text: str, reply_markup=None):
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            # Игнорируем ошибку, если сообщение не изменилось
            pass
        else:
            # Если другая ошибка - логируем её
            logger.error(f"Error editing message: {e}")

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
            await safe_edit_message(
                callback.message,
                f"👤 Профиль игрока\n\n"
                f"Имя: {callback.from_user.first_name}\n"
                f"Побед: {user.total_wins}\n"
                f"Всего звёзд: {user.total_stars:.2f} ⭐\n\n"
                f"Для пополнения баланса нажмите кнопку 'Внести оплату'\n"
                f"По всем вопросам обращайтесь в обратную связь",
                reply_markup=get_profile_keyboard()
            )
            await callback.answer()
        
        # Обработчик кнопки правил
        @dp.callback_query(lambda c: c.data == "rules")
        async def show_rules(callback: types.CallbackQuery):
            rules_text = (
                "📖 Правила игры:\n\n"
                "1. Игра ведётся на звёзды ⭐\n"
                "2. Вы делаете ставку и бросаете кости\n"
                "3. Если сумма на костях равна 10, 11 или 12 - вы выигрываете\n"
                "4. В остальных случаях - вы проигрываете\n"
                "5. При выигрыше вы получаете 2.5x от ставки\n"
                "6. При проигрыше теряете ставку\n\n"
                "Удачи в игре! 🎲"
            )
            await safe_edit_message(callback.message, rules_text, reply_markup=get_rules_keyboard())
            await callback.answer()
        
        # Обработчик возврата в главное меню
        @dp.callback_query(lambda c: c.data == "main_menu")
        async def return_to_menu(callback: types.CallbackQuery):
            await safe_edit_message(
                callback.message,
                "Главное меню\nВыберите действие:",
                reply_markup=get_main_menu_keyboard()
            )
            await callback.answer()
        
        # Обработчик кнопки оплаты
        @dp.callback_query(lambda c: c.data == "payment")
        async def show_payment(callback: types.CallbackQuery):
            await safe_edit_message(
                callback.message,
                "💳 Для пополнения баланса свяжитесь с администратором:\n"
                "@monomomn\n\n"
                "Укажите сумму пополнения и ваш ID в боте.\n"
                "После оплаты вам будет начислено 100 ⭐",
                reply_markup=get_profile_keyboard()
            )
            await callback.answer()
        
        # Обработчик кнопки игры
        @dp.callback_query(lambda c: c.data == "play")
        async def start_game(callback: types.CallbackQuery, state: FSMContext):
            user = get_or_create_user(callback.from_user.id, callback.from_user.username)
            if user.total_stars < 1:
                await safe_edit_message(
                    callback.message,
                    "❌ У вас недостаточно звёзд для игры!\n"
                    "Пополните баланс в профиле.",
                    reply_markup=get_profile_keyboard()
                )
                await callback.answer()
                return
            
            await safe_edit_message(
                callback.message,
                f"🎲 Ваш баланс: {user.total_stars:.2f} ⭐\n\n"
                "Введите сумму ставки (число):",
                reply_markup=None
            )
            await state.update_data(user_id=callback.from_user.id)
            await state.set_state(GameStates.waiting_for_bet)
            await callback.answer()
        
        # Обработчик ввода ставки
        @dp.message(GameStates.waiting_for_bet)
        async def process_bet(message: types.Message, state: FSMContext):
            try:
                bet = float(message.text)
                user = get_or_create_user(message.from_user.id, message.from_user.username)
                
                if bet <= 0:
                    await message.answer("❌ Ставка должна быть больше 0!")
                    return
                
                if bet > user.total_stars:
                    await message.answer(
                        f"❌ У вас недостаточно звёзд!\n"
                        f"Ваш баланс: {user.total_stars:.2f} ⭐",
                        reply_markup=get_main_menu_keyboard()
                    )
                    await state.clear()
                    return
                
                # Бросаем кости
                dice1 = random.randint(1, 6)
                dice2 = random.randint(1, 6)
                total = dice1 + dice2
                
                # Определяем результат
                # Теперь выигрыш если сумма равна 10, 11 или 12 (шанс выигрыша около 16.7%)
                won = total in [10, 11, 12]
                stars_won = bet * 2.5 if won else -bet  # Уменьшаем множитель выигрыша, так как шанс выигрыша больше
                
                # Обновляем статистику
                update_user_stats(message.from_user.id, stars_won, won)
                
                # Формируем сообщение о результате
                result_text = (
                    f"🎲 Результат броска:\n"
                    f"Кость 1: {dice1}\n"
                    f"Кость 2: {dice2}\n"
                    f"Сумма: {total}\n\n"
                )
                
                if won:
                    result_text += f"🎉 Поздравляем! Вы выиграли {bet * 2.5:.2f} ⭐"
                else:
                    result_text += f"😢 К сожалению, вы проигрываете {bet:.2f} ⭐"
                
                await message.answer(result_text, reply_markup=get_main_menu_keyboard())
                await state.clear()
                
            except ValueError:
                await message.answer("❌ Пожалуйста, введите корректное число!")
        
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