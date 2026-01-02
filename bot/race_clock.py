"""Модуль для работы с временем гонки и расчета текущего круга."""
from datetime import datetime
from typing import Optional

from bot.config import RACE_START_TIME, LAP_DURATION, TOTAL_LAPS


def get_current_lap(now: Optional[datetime] = None) -> Optional[int]:
    """
    Вычисляет текущий круг гонки на основе времени.
    
    Args:
        now: Текущее время (по умолчанию используется datetime.now())
    
    Returns:
        Номер текущего круга (1-12) или None, если гонка ещё не началась или уже закончилась
    """
    if RACE_START_TIME is None:
        return None
    
    if now is None:
        now = datetime.now()
    
    # Если гонка ещё не началась
    if now < RACE_START_TIME:
        return None
    
    # Вычисляем время, прошедшее с начала гонки
    elapsed_seconds = (now - RACE_START_TIME).total_seconds()
    
    # Вычисляем текущий круг (круг начинается с 1)
    current_lap = int(elapsed_seconds / LAP_DURATION) + 1
    
    # Если гонка уже закончилась
    if current_lap > TOTAL_LAPS:
        return None
    
    return current_lap


def is_race_active(now: Optional[datetime] = None) -> bool:
    """
    Проверяет, активна ли гонка в данный момент.
    
    Args:
        now: Текущее время (по умолчанию используется datetime.now())
    
    Returns:
        True, если гонка активна, False в противном случае
    """
    return get_current_lap(now) is not None


def get_race_status(now: Optional[datetime] = None) -> str:
    """
    Возвращает текстовый статус гонки.
    
    Args:
        now: Текущее время (по умолчанию используется datetime.now())
    
    Returns:
        Строка со статусом гонки
    """
    if RACE_START_TIME is None:
        return "Гонка не настроена (RACE_START_TIME не задан)"
    
    if now is None:
        now = datetime.now()
    
    current_lap = get_current_lap(now)
    
    if current_lap is None:
        if now < RACE_START_TIME:
            time_until_start = (RACE_START_TIME - now).total_seconds()
            return f"Гонка ещё не началась. До старта: {int(time_until_start)} сек"
        else:
            return "Гонка завершена"
    else:
        elapsed_seconds = (now - RACE_START_TIME).total_seconds()
        seconds_in_lap = elapsed_seconds % LAP_DURATION
        return f"Круг {current_lap}/{TOTAL_LAPS} | Время в круге: {int(seconds_in_lap)}/{LAP_DURATION} сек"

