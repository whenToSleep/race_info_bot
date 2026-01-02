"""Формирование лидерборды для гонки."""
from typing import List, Dict, Any, Optional


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

