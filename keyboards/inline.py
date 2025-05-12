from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🎲 Играть", callback_data="play"),
            InlineKeyboardButton(text="👤 Профиль", callback_data="profile")
        ],
        [
            InlineKeyboardButton(text="📖 Правила", callback_data="rules")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_profile_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="💳 Внести оплату", callback_data="payment")
        ],
        [
            InlineKeyboardButton(text="📱 Обратная связь", url="https://t.me/monomomn")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад в меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_rules_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="◀️ Назад в меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🗺 Маршруты", callback_data="routes"),
            InlineKeyboardButton(text="📚 Гайды", callback_data="guides")
        ],
        [
            InlineKeyboardButton(text="💎 Поддержать", callback_data="support"),
            InlineKeyboardButton(text="📱 Связаться", callback_data="contact")
        ]
    ]
)

routes_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🚗 Европа", callback_data="route_europe"),
            InlineKeyboardButton(text="🌍 Азия", callback_data="route_asia")
        ],
        [
            InlineKeyboardButton(text="🌎 Америка", callback_data="route_america"),
            InlineKeyboardButton(text="🌏 Австралия", callback_data="route_australia")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
        ]
    ]
)

guides_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Планирование", callback_data="guide_planning"),
            InlineKeyboardButton(text="💰 Бюджет", callback_data="guide_budget")
        ],
        [
            InlineKeyboardButton(text="🚗 Автомобиль", callback_data="guide_car"),
            InlineKeyboardButton(text="🏕 Кемпинг", callback_data="guide_camping")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
        ]
    ]
)

# Клавиатура поддержки
support_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Сделать донат", callback_data="donate"),
            InlineKeyboardButton(text="🎁 Получить бонус", callback_data="bonus")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
        ]
    ]
)

# Клавиатура контактов
contact_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📱 Telegram", url="https://t.me/your_username"),
            InlineKeyboardButton(text="📸 Instagram", url="https://instagram.com/your_username")
        ],
        [
            InlineKeyboardButton(text="🎥 YouTube", url="https://youtube.com/your_channel"),
            InlineKeyboardButton(text="🌐 Сайт", url="https://your-website.com")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
        ]
    ]
)

__all__ = [
    'main_menu_keyboard',
    'routes_keyboard',
    'guides_keyboard',
    'support_keyboard',
    'contact_keyboard'
]