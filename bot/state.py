"""Управление состоянием бота для каждого чата."""
from typing import Dict, Set, Optional


class ChatState:
    """Состояние бота для конкретного чата."""
    
    def __init__(self, chat_id: int):
        """
        Инициализация состояния чата.
        
        Args:
            chat_id: ID чата
        """
        self.chat_id = chat_id
        self.start_leaderboard_published = False
        self.published_laps: Set[int] = set()  # Множество опубликованных кругов
        self.final_leaderboard_published = False
    
    def mark_start_leaderboard_published(self):
        """Отмечает, что стартовая лидерборда опубликована."""
        self.start_leaderboard_published = True
    
    def mark_lap_published(self, lap_number: int):
        """Отмечает, что лидерборда для круга опубликована."""
        self.published_laps.add(lap_number)
    
    def is_lap_published(self, lap_number: int) -> bool:
        """Проверяет, опубликована ли лидерборда для круга."""
        return lap_number in self.published_laps
    
    def mark_final_leaderboard_published(self):
        """Отмечает, что финальная лидерборда опубликована."""
        self.final_leaderboard_published = True


class StateManager:
    """Менеджер состояний для всех чатов."""
    
    def __init__(self):
        """Инициализация менеджера состояний."""
        self._states: Dict[int, ChatState] = {}
    
    def get_state(self, chat_id: int) -> ChatState:
        """
        Получает состояние для чата, создавая его при необходимости.
        
        Args:
            chat_id: ID чата
        
        Returns:
            Состояние чата
        """
        if chat_id not in self._states:
            self._states[chat_id] = ChatState(chat_id)
        return self._states[chat_id]
    
    def reset_state(self, chat_id: int):
        """
        Сбрасывает состояние чата.
        
        Args:
            chat_id: ID чата
        """
        if chat_id in self._states:
            del self._states[chat_id]

