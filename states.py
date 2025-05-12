from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from db.models import session, User
from keyboards.inline import main_menu_keyboard, start_keyboard
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем роутер
router = Router()

# Определяем состояния
class RegistrationStates(StatesGroup):
    waiting_for_age = State()

# Обработчик начала регистрации
@router.callback_query(F.data == "start_registration")
async def register_start(callback: CallbackQuery, state: FSMContext):
    """Начало регистрации"""
    try:
        # Проверяем, не зарегистрирован ли уже пользователь
        user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
        if user:
            await callback.answer("❌ Вы уже зарегистрированы!", show_alert=True)
            return

        # Запрашиваем возраст
        await callback.message.edit_text(
            "📝 <b>Регистрация</b>\n\n"
            "Введите ваш возраст (от 18 лет):"
        )
        await state.set_state(RegistrationStates.waiting_for_age)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при начале регистрации: {e}", exc_info=True)
        await callback.message.edit_text(
            "❌ Произошла ошибка при регистрации",
            reply_markup=start_keyboard
        )
        await callback.answer("Произошла ошибка", show_alert=True)

# Обработчик ввода возраста
@router.message(RegistrationStates.waiting_for_age)
async def register_age(message: Message, state: FSMContext):
    """Обработка введенного возраста"""
    try:
        # Проверяем, что введено число
        try:
            age = int(message.text)
        except ValueError:
            await message.answer("❌ Пожалуйста, введите число!")
            return

        # Проверяем возраст
        if age < 18:
            await message.answer("❌ Извините, но бот доступен только с 18 лет!")
            return

        # Создаем нового пользователя
        user = User(
            telegram_id=message.from_user.id,
            name=message.from_user.full_name,
            age=age,
            stars=100.0  # Начальный баланс
        )
        
        # Генерируем реферальный код
        user.referral_code = user.generate_referral_code()
        
        # Сохраняем в базу
        session.add(user)
        session.commit()

        # Приветствуем пользователя
        await message.answer(
            f"✅ Регистрация успешно завершена!\n\n"
            f"👤 Ваш профиль:\n"
            f"📝 Имя: {user.name}\n"
            f"🎂 Возраст: {user.age}\n"
            f"⭐️ Баланс: {user.stars} Stars\n\n"
            f"🎮 Теперь вы можете играть!",
            reply_markup=main_menu_keyboard
        )
        
        # Очищаем состояние
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка при регистрации: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при регистрации",
            reply_markup=start_keyboard
        )
        await state.clear() 