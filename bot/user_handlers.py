"""Обработчики для работы с пользователями в личных сообщениях."""
from typing import Optional, Dict, Any, Tuple
from bot.api_client import RaceDataClient
from bot.logger import setup_logger

logger = setup_logger()


def validate_user_identifier(data: list[Dict[str, Any]], user_input: str) -> Optional[Tuple[str, str, Dict[str, Any]]]:
    """
    Валидирует ввод пользователя и находит соответствующую сущность.
    
    Args:
        data: Список всех участников гонки
        user_input: Ввод пользователя (кошелёк или название команды)
    
    Returns:
        Кортеж (entity_type, entity_value, participant_data) или None, если не найдено
        entity_type: "account" или "team"
        entity_value: значение (кошелёк или название команды)
        participant_data: данные участника
    """
    if not user_input or not user_input.strip():
        return None
    
    user_input = user_input.strip()
    
    # Проверяем, является ли ввод кошельком
    is_account = False
    if user_input.endswith('.near') or user_input.endswith('.tg'):
        is_account = True
    elif len(user_input) == 64 and all(c in '0123456789abcdef' for c in user_input.lower()):
        # Хеш длиной 64 символа (hex)
        is_account = True
    
    if is_account:
        # Ищем по полю "user" (кошелёк) - только точное совпадение
        for participant in data:
            user_field = participant.get('user', '')
            if user_field.lower() == user_input.lower():
                return ("account", user_field, participant)
    
    # Ищем по названию команды - только точное совпадение
    for participant in data:
        team_name = participant.get('team_name', '')
        if team_name.lower() == user_input.lower():
            return ("team", team_name, participant)
    
    return None

