"""Клавиатуры для бота."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Создаёт клавиатуру для выбора языка."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="language_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="language_en"),
        ],
        [
            InlineKeyboardButton(text="🇺🇦 Українська", callback_data="language_uk"),
        ]
    ])
    return keyboard

