"""Главный файл бота."""
import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER, Command
from aiogram.types import ChatMemberUpdated, Update, Message, CallbackQuery
from aiogram.client.default import DefaultBotProperties

from bot.settings import BOT_TOKEN, RACE_START_TIME, CHAT_ID
from bot.logger import setup_logger
from bot.race_clock import get_race_status, get_current_lap, is_race_active
from bot.api_client import RaceDataClient
from bot.leaderboard import format_start_leaderboard, format_lap_leaderboard
from bot.state import StateManager
from bot.user_handlers import validate_user_identifier
from bot.user_state import UserStateManager
from bot.keyboards import get_language_keyboard
from bot.config.language_config import LANGUAGE_MESSAGES, DEFAULT_LANGUAGE

# Настройка логирования
logger = setup_logger()

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Менеджер состояний для чатов
state_manager = StateManager()

# Менеджер состояний для пользователей (user-mode)
user_state_manager = UserStateManager()

# Список активных чатов (где бот добавлен)
active_chats: set[int] = set()

# Бот не обрабатывает команды в группах - только публикует сообщения автоматически
# В личных сообщениях обрабатывает ввод пользователя (user-mode)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start в личных сообщениях."""
    if message.chat.type != "private":
        return
    
    # Всегда показываем выбор языка на английском при первом запуске
    messages = LANGUAGE_MESSAGES["en"]
    await message.answer(
        messages["choose_language"],
        reply_markup=get_language_keyboard()
    )


@dp.callback_query(lambda c: c.data and c.data.startswith("language_"))
async def process_language_choice(callback: CallbackQuery):
    """Обработчик выбора языка."""
    try:
        language = callback.data.split("_")[1]
        user_id = callback.from_user.id
        
        # Сохраняем выбор языка
        user_state_manager.set_language(user_id, language)
        
        # Показываем начальное сообщение на выбранном языке
        messages = LANGUAGE_MESSAGES[language]
        await callback.message.edit_text(messages["start"])
        
        # Уведомление на выбранном языке
        lang_names = {"ru": "Русский", "en": "English", "uk": "Українська"}
        await callback.answer(f"Language: {lang_names.get(language, language.upper())}")
    except Exception as e:
        logger.error(f"Ошибка в process_language_choice: {e}", exc_info=True)
        await callback.answer("Произошла ошибка. Попробуйте позже.")


@dp.message(Command("language"))
async def cmd_language(message: Message):
    """Обработчик команды /language для смены языка."""
    if message.chat.type != "private":
        return
    
    # Показываем выбор языка на английском
    messages = LANGUAGE_MESSAGES["en"]
    await message.answer(
        messages["choose_language"],
        reply_markup=get_language_keyboard()
    )


@dp.message(lambda m: m.chat.type == "private" and m.text and not m.text.startswith('/'))
async def handle_user_input(message: Message):
    """Обработчик ввода пользователя в личных сообщениях (user-mode)."""
    user_id = message.from_user.id
    user_input = message.text.strip()
    user_state = user_state_manager.get_state(user_id)
    language = user_state.language
    messages = LANGUAGE_MESSAGES[language]
    
    logger.info(f"Пользователь {user_id} ввёл: {user_input}")
    
    try:
        # Загружаем данные гонки
        api_client = RaceDataClient()
        data = api_client.get_data()
        
        # Валидируем ввод пользователя
        result = validate_user_identifier(data, user_input)
        
        if result is None:
            # Сущность не найдена
            await message.answer(messages["not_found"].format(input=user_input))
            return
        
        entity_type, entity_value, participant_data = result
        
        # Сохраняем выбор пользователя
        user_state_manager.set_tracked_entity(user_id, entity_type, entity_value)
        
        # Формируем сообщение
        entity_display = messages[entity_type].format(value=entity_value)
        await message.answer(
            messages["found"].format(
                entity_display=entity_display,
                team_name=participant_data.get('team_name', 'Unknown'),
                start_position=participant_data.get('start_position', 0)
            )
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке ввода пользователя {user_id}: {e}", exc_info=True)
        await message.answer(messages["error"])


@dp.message()
async def on_any_message(message: Message):
    """Обработчик любых сообщений для регистрации чатов (group-mode)."""
    chat_id = message.chat.id
    
    # Пропускаем личные сообщения (они обрабатываются отдельно)
    if message.chat.type == "private":
        return
    
    # Для групп/каналов - регистрируем чат
    chat_title = message.chat.title or "группа"
    
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


async def send_lap_leaderboard(chat_id: int, lap_number: int):
    """Отправляет лидерборду для конкретного круга в чат."""
    try:
        state = state_manager.get_state(chat_id)
        
        # Проверяем, не опубликована ли уже лидерборда для этого круга
        if state.is_lap_published(lap_number):
            return
        
        # Загружаем данные и формируем лидерборду
        api_client = RaceDataClient()
        participants = api_client.get_participants_sorted_by_lap(lap_number)
        leaderboard_text = format_lap_leaderboard(participants, lap_number)
        
        # Отправляем сообщение
        await bot.send_message(chat_id=chat_id, text=leaderboard_text)
        
        # Отмечаем, что лидерборда для круга опубликована
        state.mark_lap_published(lap_number)
        logger.info(f"✅ Лидерборда для круга {lap_number} отправлена в чат {chat_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке лидерборды для круга {lap_number} в чат {chat_id}: {e}", exc_info=True)


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


async def check_and_send_lap_leaderboards():
    """Проверяет и отправляет лидерборды для завершенных кругов (в конце круга)."""
    if RACE_START_TIME is None:
        return
    
    # Получаем список чатов для отправки
    chat_ids = set()
    if CHAT_ID:
        chat_ids.add(CHAT_ID)
    chat_ids.update(active_chats)
    
    if not chat_ids:
        return
    
    # Храним предыдущий круг для отслеживания изменений
    if not hasattr(check_and_send_lap_leaderboards, '_previous_lap'):
        check_and_send_lap_leaderboards._previous_lap = None
    
    # Проверяем текущий круг
    current_lap = get_current_lap()
    
    # Если круг изменился, значит предыдущий круг завершился
    if check_and_send_lap_leaderboards._previous_lap is not None:
        if current_lap != check_and_send_lap_leaderboards._previous_lap:
            # Круг изменился - отправляем лидерборду для завершенного круга
            completed_lap = check_and_send_lap_leaderboards._previous_lap
            for chat_id in chat_ids:
                await send_lap_leaderboard(chat_id, completed_lap)
    
    # Если гонка завершена (current_lap = None), но предыдущий круг был 12
    if current_lap is None and check_and_send_lap_leaderboards._previous_lap == 12:
        # Отправляем лидерборду для 12-го круга (финальная)
        for chat_id in chat_ids:
            await send_lap_leaderboard(chat_id, 12)
    
    # Сохраняем текущий круг для следующей проверки
    check_and_send_lap_leaderboards._previous_lap = current_lap




async def log_race_status():
    """Периодически логирует статус гонки каждые 5 секунд и проверяет отправку лидерборд."""
    while True:
        try:
            status = get_race_status()
            logger.info(f"Статус гонки: {status}")
            
            # Проверяем и отправляем стартовую лидерборду при старте гонки
            await check_and_send_start_leaderboard()
            
            # Проверяем и отправляем лидерборды для завершенных кругов (в конце круга)
            await check_and_send_lap_leaderboards()
            
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

