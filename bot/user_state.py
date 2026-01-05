"""Управление состоянием пользователей (user-mode)."""
from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class UserState:
    """Состояние пользователя для отслеживания."""
    user_id: int
    language: str = "ru"  # Язык интерфейса
    entity_type: Optional[str] = None  # "account" или "team"
    entity_value: Optional[str] = None  # Значение (кошелёк или название команды)
    last_sent_lap: int = 0  # Последний отправленный круг
    is_tracking: bool = False  # Активно ли отслеживание


class UserStateManager:
    """Менеджер состояний пользователей."""
    
    def __init__(self):
        """Инициализация менеджера состояний."""
        self._states: Dict[int, UserState] = {}
    
    def get_state(self, user_id: int) -> UserState:
        """
        Получает состояние пользователя, создавая его при необходимости.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Состояние пользователя
        """
        if user_id not in self._states:
            self._states[user_id] = UserState(user_id=user_id)
        return self._states[user_id]
    
    def set_language(self, user_id: int, language: str):
        """
        Устанавливает язык для пользователя.
        
        Args:
            user_id: ID пользователя
            language: Код языка (ru, en, uk)
        """
        state = self.get_state(user_id)
        state.language = language
    
    def set_tracked_entity(self, user_id: int, entity_type: str, entity_value: str):
        """
        Устанавливает отслеживаемую сущность для пользователя.
        
        Args:
            user_id: ID пользователя
            entity_type: Тип сущности ("account" или "team")
            entity_value: Значение (кошелёк или название команды)
        """
        state = self.get_state(user_id)
        state.entity_type = entity_type
        state.entity_value = entity_value
    
    def reset_state(self, user_id: int):
        """
        Сбрасывает состояние пользователя.
        
        Args:
            user_id: ID пользователя
        """
        if user_id in self._states:
            del self._states[user_id]

