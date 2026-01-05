"""Формирование лидерборды для гонки."""
from typing import List, Dict, Any, Optional
from bot.user_handlers import find_user_position, slice_leaderboard
from bot.config.language_config import LANGUAGE_MESSAGES


def format_start_leaderboard(participants: List[Dict[str, Any]]) -> str:
    """
    Формирует стартовую лидерборду по стартовым позициям.
    
    Args:
        participants: Список участников, отсортированных по start_position
    
    Returns:
        Отформатированная строка с лидербордой
    """
    if not participants:
        return "Нет данных об участниках"
    
    lines = ["🏁 <b>СТАРТОВАЯ ПОЗИЦИЯ</b>\n"]
    
    # Показываем всех участников
    for idx, participant in enumerate(participants, 1):
        team_name = participant.get('team_name', 'Unknown')
        
        # Форматируем позицию с эмодзи
        if idx == 1:
            emoji = "🥇"
        elif idx == 2:
            emoji = "🥈"
        elif idx == 3:
            emoji = "🥉"
        else:
            emoji = f"{idx}."
        
        lines.append(f"{emoji} <b>{team_name}</b>")
    
    return "\n".join(lines)


def format_lap_leaderboard(participants: List[Dict[str, Any]], lap_number: int) -> str:
    """
    Формирует лидерборду для конкретного круга.
    
    Args:
        participants: Список участников, отсортированных по позиции на круге
        lap_number: Номер круга
    
    Returns:
        Отформатированная строка с лидербордой
    """
    if not participants:
        return f"Нет данных для круга {lap_number}"
    
    lines = [f"🏁 <b>КРУГ {lap_number}</b>\n"]
    
    # Для первого круга сравниваем со стартовой позицией
    # Для остальных кругов - с предыдущим кругом
    previous_lap_key = f"lap{lap_number - 1}" if lap_number > 1 else None
    
    # Показываем всех участников
    for idx, participant in enumerate(participants, 1):
        team_name = participant.get('team_name', 'Unknown')
        lap_position = participant.get(f'lap{lap_number}', 0)
        
        # Форматируем позицию с эмодзи
        if idx == 1:
            emoji = "🥇"
        elif idx == 2:
            emoji = "🥈"
        elif idx == 3:
            emoji = "🥉"
        else:
            emoji = f"{idx}."
        
        # Вычисляем изменение позиции
        if lap_number == 1:
            # Для первого круга сравниваем со стартовой позицией
            start_pos = participant.get('start_position', 0)
            position_change = start_pos - lap_position
        else:
            # Для остальных кругов сравниваем с предыдущим кругом
            previous_lap_position = participant.get(previous_lap_key, lap_position)
            position_change = previous_lap_position - lap_position
        
        # Форматируем изменение позиции
        if position_change > 0:
            change_str = f"⬆️ +{position_change}"
        elif position_change < 0:
            change_str = f"⬇️ {position_change}"
        else:
            change_str = "➡️ 0"
        
        lines.append(f"{emoji} <b>{team_name}</b> ({change_str})")
    
    return "\n".join(lines)


def format_final_leaderboard(participants: List[Dict[str, Any]]) -> str:
    """
    Формирует финальную лидерборду по результатам последнего круга.
    
    Args:
        participants: Список участников, отсортированных по финальной позиции
    
    Returns:
        Отформатированная строка с финальной лидербордой
    """
    if not participants:
        return "Нет данных о финальных результатах"
    
    lines = ["🏁 <b>ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ</b>\n"]
    
    # Показываем всех участников
    for idx, participant in enumerate(participants, 1):
        team_name = participant.get('team_name', 'Unknown')
        final_position = participant.get('lap12', 0)
        start_pos = participant.get('start_position', 0)
        
        # Форматируем позицию с эмодзи
        if idx == 1:
            emoji = "🥇"
        elif idx == 2:
            emoji = "🥈"
        elif idx == 3:
            emoji = "🥉"
        else:
            emoji = f"{idx}."
        
        # Показываем изменение позиции относительно старта
        position_change = start_pos - final_position
        if position_change > 0:
            change_str = f"⬆️ +{position_change}"
        elif position_change < 0:
            change_str = f"⬇️ {position_change}"
        else:
            change_str = "➡️ 0"
        
        lines.append(f"{emoji} <b>{team_name}</b> (финал: {final_position}, {change_str})")
    
    return "\n".join(lines)


def format_user_leaderboard(
    leaderboard: List[Dict[str, Any]], 
    lap_number: int, 
    total_laps: int,
    entity_type: str, 
    entity_value: str,
    previous_lap_leaderboard: Optional[List[Dict[str, Any]]] = None,
    language: str = "ru"
) -> str:
    """
    Формирует персональную лидерборду для пользователя с окном ±5 позиций.
    
    Args:
        leaderboard: Полный список участников, отсортированных по позиции на круге
        lap_number: Номер текущего круга
        total_laps: Общее количество кругов
        entity_type: Тип сущности ("account" или "team")
        entity_value: Значение (кошелёк или название команды)
        previous_lap_leaderboard: Лидерборда предыдущего круга (для расчёта изменения позиции)
        language: Язык для переводов (ru, en, uk)
    
    Returns:
        Отформатированная строка с персональной лидербордой
    """
    messages = LANGUAGE_MESSAGES.get(language, LANGUAGE_MESSAGES["ru"])
    
    if not leaderboard:
        return messages["no_data_lap"].format(lap_number=lap_number)
    
    # Находим позицию пользователя
    position_result = find_user_position(leaderboard, entity_type, entity_value)
    if position_result is None:
        return f"Участник не найден в лидерборде для круга {lap_number}"
    
    user_position, user_index = position_result
    
    # Создаём окно ±5 позиций
    window_leaderboard, start_idx, end_idx = slice_leaderboard(leaderboard, user_index, window_size=5)
    
    # Формируем заголовок с отступом сверху
    lines = [f"\n🏁 {messages['lap']} {lap_number} / {total_laps}\n"]
    
    # Вычисляем изменение позиции относительно предыдущего круга
    position_change = None
    if previous_lap_leaderboard is not None:
        # Находим позицию на предыдущем круге
        prev_position_result = find_user_position(previous_lap_leaderboard, entity_type, entity_value)
        if prev_position_result is not None:
            prev_position, _ = prev_position_result
            position_change = prev_position - user_position
    
    # Добавляем информацию о позиции пользователя
    change_str = ""
    if position_change is not None:
        if position_change > 0:
            change_str = f" ⬆️ +{position_change}"
        elif position_change < 0:
            change_str = f" ⬇️ {position_change}"
        else:
            change_str = " ➡️ 0"
    
    lines.append(f"➡️ {messages['you_place'].format(position=user_position)}{change_str}\n")
    
    # Форматируем участников в окне
    for idx, participant in enumerate(window_leaderboard):
        actual_position = start_idx + idx + 1  # Позиция в полной лидерборде (1-based)
        team_name = participant.get('team_name', 'Unknown')
        
        # Проверяем, это ли пользователь
        is_user = False
        if entity_type == "account":
            is_user = participant.get('user', '').lower() == entity_value.lower()
        elif entity_type == "team":
            is_user = participant.get('team_name', '').lower() == entity_value.lower()
        
        # Форматируем позицию
        if is_user:
            # Выделяем пользователя с отступами сверху и снизу
            lines.append("")  # Отступ сверху
            lines.append(f"{actual_position}. 🔥 <b>{team_name}</b>")
            lines.append("")  # Отступ снизу
        else:
            lines.append(f"{actual_position}. {team_name}")
    
    return "\n".join(lines)

