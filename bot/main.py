"""Главный файл бота."""
import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER
from aiogram.types import ChatMemberUpdated, Update, Message
from aiogram.client.default import DefaultBotProperties

from bot.config import BOT_TOKEN, RACE_START_TIME, CHAT_ID
from bot.logger import setup_logger
from bot.race_clock import get_race_status, get_current_lap, is_race_active
from bot.api_client import RaceDataClient
from bot.leaderboard import format_start_leaderboard
from bot.state import StateManager

# Настройка логирования
logger = setup_logger()

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Менеджер состояний для чатов
state_manager = StateManager()

# Список активных чатов (где бот добавлен)
active_chats: set[int] = set()

# Бот не обрабатывает команды - только публикует сообщения автоматически


@dp.message()
async def on_any_message(message: Message):
    """Обработчик любых сообщений для регистрации чатов, где бот уже находится."""
    chat_id = message.chat.id
    chat_title = message.chat.title or message.chat.first_name or "личный чат"
    
    # Регистрируем чат, если он ещё не зарегистрирован
    if chat_id not in active_chats:
        active_chats.add(chat_id)
        logger.info(f"📝 Обнаружен чат {chat_id} ({chat_title}) через сообщение")
        logger.info(f"📋 Теперь активных чатов: {len(active_chats)}")
        
        # Если гонка уже началась, отправляем стартовую лидерборду
        if is_race_active():
            logger.info(f"Гонка активна, отправляем стартовую лидерборду в чат {chat_id}")
            await send_start_leaderboard(chat_id)
    else:
        # Логируем первые несколько сообщений для отладки
        if not hasattr(on_any_message, '_log_count'):
            on_any_message._log_count = {}
        if chat_id not in on_any_message._log_count:
            on_any_message._log_count[chat_id] = 0
        on_any_message._log_count[chat_id] += 1
        if on_any_message._log_count[chat_id] <= 2:
            logger.debug(f"Сообщение из известного чата {chat_id} ({chat_title})")


@dp.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_bot_added_to_chat(event: ChatMemberUpdated):
    """Обработчик добавления бота в чат (my_chat_member - для самого бота)."""
    chat_id = event.chat.id
    active_chats.add(chat_id)
    chat_title = event.chat.title or 'личный чат'
    logger.info(f"🤖 Бот добавлен в чат {chat_id} ({chat_title})")
    logger.info(f"📋 Теперь активных чатов: {len(active_chats)}")
    
    # Если гонка уже началась, отправляем стартовую лидерборду
    if is_race_active():
        logger.info(f"Гонка активна, отправляем стартовую лидерборду в чат {chat_id}")
        await send_start_leaderboard(chat_id)
    else:
        logger.info(f"Гонка ещё не началась, стартовая лидерборда будет отправлена при старте")


async def send_start_leaderboard(chat_id: int):
    """Отправляет стартовую лидерборду в чат."""
    try:
        state = state_manager.get_state(chat_id)
        
        # Проверяем, не опубликована ли уже стартовая лидерборда
        if state.start_leaderboard_published:
            return
        
        # Загружаем данные и формируем лидерборду
        api_client = RaceDataClient()
        participants = api_client.get_participants_sorted_by_start_position()
        leaderboard_text = format_start_leaderboard(participants)
        
        # Отправляем сообщение
        await bot.send_message(chat_id=chat_id, text=leaderboard_text)
        
        # Отмечаем, что стартовая лидерборда опубликована
        state.mark_start_leaderboard_published()
        logger.info(f"✅ Стартовая лидерборда отправлена в чат {chat_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке стартовой лидерборды в чат {chat_id}: {e}", exc_info=True)


async def check_and_send_start_leaderboard():
    """Проверяет и отправляет стартовую лидерборду при старте гонки."""
    if RACE_START_TIME is None:
        return
    
    # Получаем список чатов для отправки
    chat_ids = set()
    if CHAT_ID:
        chat_ids.add(CHAT_ID)
    # Добавляем активные чаты (где бот добавлен)
    chat_ids.update(active_chats)
    
    # Логируем информацию о чатах только раз в 30 секунд
    if not hasattr(check_and_send_start_leaderboard, '_last_log_time'):
        check_and_send_start_leaderboard._last_log_time = 0
    
    import time
    current_time = time.time()
    if current_time - check_and_send_start_leaderboard._last_log_time >= 30:
        if CHAT_ID:
            logger.info(f"📋 Используется CHAT_ID из конфига: {CHAT_ID}")
        if active_chats:
            logger.info(f"📋 Активные чаты (обнаружены автоматически): {active_chats}")
        if not chat_ids:
            logger.warning("⚠️ Нет чатов для отправки! Укажите CHAT_ID в .env или отправьте сообщение в чат, где находится бот")
        check_and_send_start_leaderboard._last_log_time = current_time
    
    if not chat_ids:
        return
    
    # Проверяем, началась ли гонка
    race_active = is_race_active()
    
    if not race_active:
        return
    
    logger.info(f"🏁 Гонка началась! Отправляем стартовую лидерборду в чаты: {chat_ids}")
    # Отправляем стартовую лидерборду во все чаты
    for chat_id in chat_ids:
        await send_start_leaderboard(chat_id)


async def log_race_status():
    """Периодически логирует статус гонки каждые 5 секунд и проверяет отправку стартовой лидерборды."""
    while True:
        try:
            status = get_race_status()
            logger.info(f"Статус гонки: {status}")
            
            # Проверяем и отправляем стартовую лидерборду при старте гонки
            await check_and_send_start_leaderboard()
            
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
        
        # Показываем информацию о чатах
        if CHAT_ID:
            active_chats.add(CHAT_ID)
            logger.info(f"📋 CHAT_ID указан в конфиге: {CHAT_ID} (добавлен в активные чаты)")
        else:
            logger.info("📋 CHAT_ID не указан. Бот будет регистрировать чаты автоматически при получении обновлений.")
            logger.info("💡 Подсказка: отправьте любое сообщение в чат, где находится бот, чтобы он его зарегистрировал")
            logger.info("💡 Или укажите CHAT_ID в .env файле для автоматической отправки")
        
        # Запускаем задачу логирования статуса гонки
        log_task = asyncio.create_task(log_race_status())
        
        # Запускаем polling
        logger.info("🔄 Запуск polling... Ожидание обновлений...")
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

