from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    kb = [
        [
            KeyboardButton(text="📋 Мои задачи"),
            KeyboardButton(text="🚗 Мои поездки")
        ],
        [
            KeyboardButton(text="👤 Профиль")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_auth_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🚀 Начать регистрацию")]], resize_keyboard=True)
