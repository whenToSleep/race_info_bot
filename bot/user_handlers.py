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


def find_user_position(leaderboard: list[Dict[str, Any]], entity_type: str, entity_value: str) -> Optional[Tuple[int, int]]:
    """
    Находит позицию пользователя в лидерборде.
    
    Args:
        leaderboard: Список участников, отсортированных по позиции
        entity_type: Тип сущности ("account" или "team")
        entity_value: Значение (кошелёк или название команды)
    
    Returns:
        Кортеж (позиция, индекс) или None, если не найдено
        позиция: позиция в лидерборде (1-based)
        индекс: индекс в массиве (0-based)
    """
    for idx, participant in enumerate(leaderboard):
        if entity_type == "account":
            # Ищем по кошельку
            if participant.get('user', '').lower() == entity_value.lower():
                return (idx + 1, idx)
        elif entity_type == "team":
            # Ищем по названию команды
            if participant.get('team_name', '').lower() == entity_value.lower():
                return (idx + 1, idx)
    
    return None


def slice_leaderboard(leaderboard: list[Dict[str, Any]], user_index: int, window_size: int = 5) -> Tuple[list[Dict[str, Any]], int, int]:
    """
    Создаёт окно лидерборды вокруг позиции пользователя.
    
    Args:
        leaderboard: Полный список участников, отсортированных по позиции
        user_index: Индекс пользователя в массиве (0-based)
        window_size: Размер окна в каждую сторону (по умолчанию 5)
    
    Returns:
        Кортеж (срез лидерборды, начальный индекс, конечный индекс)
        срез: список участников в окне
        начальный_индекс: начальный индекс в исходном массиве (0-based)
        конечный_индекс: конечный индекс в исходном массиве (0-based, не включительно)
    """
    if not leaderboard or user_index < 0 or user_index >= len(leaderboard):
        return ([], 0, 0)
    
    # Вычисляем границы окна
    start_idx = max(0, user_index - window_size)
    end_idx = min(len(leaderboard), user_index + window_size + 1)
    
    # Возвращаем срез и границы
    return (leaderboard[start_idx:end_idx], start_idx, end_idx)

