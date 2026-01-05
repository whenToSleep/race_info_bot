"""Клавиатуры для бота."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from bot.config.language_config import LANGUAGE_MESSAGES


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


def get_stop_tracking_keyboard(language: str = "ru") -> ReplyKeyboardMarkup:
    """Создаёт reply клавиатуру с кнопкой 'Прекратить отслеживание'."""
    messages = LANGUAGE_MESSAGES.get(language, LANGUAGE_MESSAGES["ru"])
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=messages["stop_tracking"])]],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


def get_empty_keyboard() -> ReplyKeyboardRemove:
    """Убирает reply клавиатуру."""
    return ReplyKeyboardRemove()

