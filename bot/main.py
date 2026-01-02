"""Главный файл бота."""
import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from bot.config import BOT_TOKEN, RACE_START_TIME
from bot.logger import setup_logger
from bot.race_clock import get_race_status
from bot.api_client import RaceDataClient

# Настройка логирования
logger = setup_logger()

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Бот не обрабатывает команды - только публикует сообщения автоматически


async def log_race_status():
    """Периодически логирует статус гонки каждые 5 секунд."""
    while True:
        try:
            status = get_race_status()
            logger.info(f"Статус гонки: {status}")
        except Exception as e:
            logger.error(f"Ошибка при получении статуса гонки: {e}", exc_info=True)
        
        await asyncio.sleep(5)


async def main():
    """Главная функция запуска бота."""
    logger.info("Запуск бота...")
    
    if RACE_START_TIME is None:
        logger.warning("RACE_START_TIME не задан в .env. Бот будет работать, но гонка не настроена.")
    else:
        logger.info(f"Время старта гонки: {RACE_START_TIME}")
    
    # Проверяем загрузку данных гонки
    try:
        api_client = RaceDataClient()
        data = api_client.load_data()
        logger.info(f"Данные гонки загружены: {len(data)} участников")
        
        # Проверяем сортировку по start_position
        sorted_by_start = api_client.get_participants_sorted_by_start_position()
        if sorted_by_start:
            logger.info(f"Первый участник по стартовой позиции: {sorted_by_start[0]['team_name']} (позиция {sorted_by_start[0]['start_position']})")
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных гонки: {e}", exc_info=True)
        logger.warning("Бот продолжит работу, но данные гонки недоступны")
    
    try:
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"Бот запущен: @{bot_info.username} (ID: {bot_info.id})")
        
        # Запускаем задачу логирования статуса гонки
        log_task = asyncio.create_task(log_race_status())
        
        # Запускаем polling
        await dp.start_polling(bot)
        
        # Отменяем задачу логирования при остановке
        log_task.cancel()
        try:
            await log_task
        except asyncio.CancelledError:
            pass
            
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки (Ctrl+C)")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)

