"""Конфигурация бота."""
import os
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения. Проверьте файл .env")

# Параметры гонки
# Время старта гонки (задаётся вручную, формат: "YYYY-MM-DD HH:MM:SS")
# Пример: "2024-01-15 14:30:00"
RACE_START_TIME_STR = os.getenv("RACE_START_TIME", "")

# Длительность одного круга в секундах
LAP_DURATION = 20

# Общее количество кругов
TOTAL_LAPS = 12

# Преобразуем строку времени старта в datetime
RACE_START_TIME = None
if RACE_START_TIME_STR:
    try:
        RACE_START_TIME = datetime.strptime(RACE_START_TIME_STR, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError(
            f"Неверный формат RACE_START_TIME: '{RACE_START_TIME_STR}'. "
            f"Используйте формат: 'YYYY-MM-DD HH:MM:SS'"
        )

# ID чата для отправки сообщений (опционально, можно указать в .env)
# Если не указан, бот будет отправлять в чаты, где он добавлен
# CHAT_ID может быть отрицательным для групп
CHAT_ID_STR = os.getenv("CHAT_ID", "").strip()
CHAT_ID = None
if CHAT_ID_STR:
    try:
        # Пробуем преобразовать в int (может быть отрицательным)
        CHAT_ID = int(CHAT_ID_STR)
    except ValueError:
        # Если не удалось преобразовать, оставляем None
        CHAT_ID = None

