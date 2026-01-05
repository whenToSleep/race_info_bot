"""Конфигурация языков для бота."""
LANGUAGE_MESSAGES = {
    "ru": {
        "start": (
            "🏁 <b>Добро пожаловать в бот отслеживания гонок!</b>\n\n"
            "Введите ваш кошелёк или название команды для отслеживания позиции во время гонки.\n\n"
            "<b>Формат кошелька:</b>\n"
            "• Оканчивается на <code>.near</code> или <code>.tg</code>\n"
            "• Или имеет длину 64 символа\n\n"
            "<b>Важно:</b> Если кошелька или названия команды нет в списке участников, отслеживание невозможно."
        ),
        "choose_language": (
            "🌐 <b>Выберите язык</b>\n\n"
            "Выберите язык для взаимодействия с ботом:"
        ),
        "not_found": (
            "❌ Не найдено: <b>{input}</b>\n\n"
            "<b>Формат кошелька:</b>\n"
            "• Оканчивается на <code>.near</code> или <code>.tg</code>\n"
            "• Или имеет длину 64 символа\n\n"
            "<b>Важно:</b> Если кошелька или названия команды нет в списке участников, отслеживание невозможно.\n\n"
            "Проверьте правильность ввода и попробуйте снова."
        ),
        "found": (
            "✅ Найдено: {entity_display}\n\n"
            "Команда: <b>{team_name}</b>\n"
            "Стартовая позиция: {start_position}\n\n"
            "Отслеживание начато! Вы будете получать обновления по каждому кругу."
        ),
        "stop_tracking": "Прекратить отслеживание",
        "tracking_stopped": "Отслеживание прекращено.",
        "tracking_already_active": "Отслеживание уже активно для: {entity_display}",
        "tracking_not_active": "Отслеживание не активно.",
        "error": "❌ Произошла ошибка при обработке запроса. Попробуйте позже.",
        "account": "кошелёк <b>{value}</b>",
        "team": "команда <b>{value}</b>",
        "current_language_warning": "Внимание! Контент будет отображаться на выбранном языке. Убедитесь, что язык выбран правильно.\nТекущий язык: {language}",
        "change_language": "Изменить язык",
        "keep_current": "Оставить текущий",
        "start_leaderboard": "🏁 <b>СТАРТОВАЯ ПОЗИЦИЯ</b>\n",
        "lap_leaderboard": "🏁 <b>КРУГ {lap_number}</b>\n",
        "no_data": "Нет данных об участниках",
        "no_data_lap": "Нет данных для круга {lap_number}",
        "lap": "Круг",
        "you_place": "Вы: {position} место",
    },
    "en": {
        "start": (
            "🏁 <b>Welcome to the race tracking bot!</b>\n\n"
            "Enter your wallet or team name to track your position during the race.\n\n"
            "<b>Wallet format:</b>\n"
            "• Ends with <code>.near</code> or <code>.tg</code>\n"
            "• Or has a length of 64 characters\n\n"
            "<b>Important:</b> If the wallet or team name is not in the participants list, tracking is not possible."
        ),
        "choose_language": (
            "🌐 <b>Choose your language</b>\n\n"
            "Select the language for bot interaction:"
        ),
        "not_found": (
            "❌ Not found: <b>{input}</b>\n\n"
            "<b>Wallet format:</b>\n"
            "• Ends with <code>.near</code> or <code>.tg</code>\n"
            "• Or has a length of 64 characters\n\n"
            "<b>Important:</b> If the wallet or team name is not in the participants list, tracking is not possible.\n\n"
            "Check the input and try again."
        ),
        "found": (
            "✅ Found: {entity_display}\n\n"
            "Team: <b>{team_name}</b>\n"
            "Start position: {start_position}\n\n"
            "Tracking started! You will receive updates for each lap."
        ),
        "stop_tracking": "Stop Tracking",
        "tracking_stopped": "Tracking stopped.",
        "tracking_already_active": "Tracking is already active for: {entity_display}",
        "tracking_not_active": "Tracking is not active.",
        "error": "❌ An error occurred while processing the request. Please try again later.",
        "account": "wallet <b>{value}</b>",
        "team": "team <b>{value}</b>",
        "current_language_warning": "Warning! Content will be displayed in the selected language. Make sure the language is correct.\nCurrent language: {language}",
        "change_language": "Change Language",
        "keep_current": "Keep Current",
        "start_leaderboard": "🏁 <b>STARTING POSITION</b>\n",
        "lap_leaderboard": "🏁 <b>LAP {lap_number}</b>\n",
        "no_data": "No participant data",
        "no_data_lap": "No data for lap {lap_number}",
        "lap": "Lap",
        "you_place": "You: {position} place",
    },
    "uk": {
        "start": (
            "🏁 <b>Ласкаво просимо до бота відстеження гонок!</b>\n\n"
            "Введіть ваш гаманець або назву команди для відстеження позиції під час гонки.\n\n"
            "<b>Формат гаманця:</b>\n"
            "• Закінчується на <code>.near</code> або <code>.tg</code>\n"
            "• Або має довжину 64 символи\n\n"
            "<b>Важливо:</b> Якщо гаманця або назви команди немає в списку учасників, відстеження неможливе."
        ),
        "choose_language": (
            "🌐 <b>Оберіть мову</b>\n\n"
            "Виберіть мову для взаємодії з ботом:"
        ),
        "not_found": (
            "❌ Не знайдено: <b>{input}</b>\n\n"
            "<b>Формат гаманця:</b>\n"
            "• Закінчується на <code>.near</code> або <code>.tg</code>\n"
            "• Або має довжину 64 символи\n\n"
            "<b>Важливо:</b> Якщо гаманця або назви команди немає в списку учасників, відстеження неможливе.\n\n"
            "Перевірте правильність введення та спробуйте знову."
        ),
        "found": (
            "✅ Знайдено: {entity_display}\n\n"
            "Команда: <b>{team_name}</b>\n"
            "Стартова позиція: {start_position}\n\n"
            "Відстеження розпочато! Ви будете отримувати оновлення по кожному колу."
        ),
        "stop_tracking": "Припинити відстеження",
        "tracking_stopped": "Відстеження припинено.",
        "tracking_already_active": "Відстеження вже активне для: {entity_display}",
        "tracking_not_active": "Відстеження не активне.",
        "error": "❌ Сталася помилка під час обробки запиту. Спробуйте пізніше.",
        "account": "гаманець <b>{value}</b>",
        "team": "команда <b>{value}</b>",
        "current_language_warning": "Увага! Контент буде відображатися на вибраній мові. Переконайтеся, що обрано правильну мову.\nПоточна мова: {language}",
        "change_language": "Поміняти мову",
        "keep_current": "Залишити поточну",
        "start_leaderboard": "🏁 <b>СТАРТОВА ПОЗИЦІЯ</b>\n",
        "lap_leaderboard": "🏁 <b>КРУГ {lap_number}</b>\n",
        "no_data": "Немає даних про учасників",
        "no_data_lap": "Немає даних для круга {lap_number}",
        "lap": "Круг",
        "you_place": "Ви: {position} місце",
    }
}

# Язык по умолчанию
DEFAULT_LANGUAGE = "ru"

