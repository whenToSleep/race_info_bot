"""Клиент для работы с API данных гонки."""
import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from bot.logger import setup_logger

logger = setup_logger()


class RaceDataClient:
    """Клиент для загрузки и работы с данными гонки."""
    
    def __init__(self, json_file_path: Optional[str] = None):
        """
        Инициализация клиента.
        
        Args:
            json_file_path: Путь к JSON файлу с данными. 
                          По умолчанию используется race_2_results.json в корне проекта.
        """
        if json_file_path is None:
            # Путь к файлу относительно корня проекта
            project_root = Path(__file__).parent.parent
            json_file_path = project_root / "race_2_results.json"
        
        self.json_file_path = Path(json_file_path)
        self._data: Optional[List[Dict[str, Any]]] = None
    
    def load_data(self) -> List[Dict[str, Any]]:
        """
        Загружает данные из JSON файла.
        
        Returns:
            Список словарей с данными участников гонки
        
        Raises:
            FileNotFoundError: Если файл не найден
            json.JSONDecodeError: Если файл содержит невалидный JSON
        """
        if not self.json_file_path.exists():
            raise FileNotFoundError(f"Файл с данными не найден: {self.json_file_path}")
        
        logger.info(f"Загрузка данных из {self.json_file_path}")
        
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("Данные должны быть списком объектов")
            
            # Валидация структуры данных
            self._validate_data(data)
            
            self._data = data
            logger.info(f"Загружено {len(data)} участников")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных: {e}")
            raise
    
    def _validate_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Валидирует структуру данных.
        
        Args:
            data: Список словарей с данными участников
        
        Raises:
            ValueError: Если структура данных невалидна
        """
        required_fields = ['user', 'team_name', 'start_position']
        
        for idx, participant in enumerate(data):
            if not isinstance(participant, dict):
                raise ValueError(f"Участник #{idx} должен быть словарём")
            
            for field in required_fields:
                if field not in participant:
                    raise ValueError(f"У участника #{idx} отсутствует поле '{field}'")
            
            # Проверяем, что start_position - число
            if not isinstance(participant['start_position'], int):
                raise ValueError(f"У участника #{idx} start_position должен быть числом")
            
            # Проверяем наличие полей lap1-lap12
            for lap_num in range(1, 13):
                lap_key = f"lap{lap_num}"
                if lap_key not in participant:
                    logger.warning(f"У участника #{idx} отсутствует поле '{lap_key}'")
    
    def get_data(self, reload: bool = False) -> List[Dict[str, Any]]:
        """
        Получает загруженные данные.
        
        Args:
            reload: Если True, перезагружает данные из файла
        
        Returns:
            Список словарей с данными участников
        """
        if self._data is None or reload:
            return self.load_data()
        
        return self._data
    
    def get_participants_sorted_by_start_position(self) -> List[Dict[str, Any]]:
        """
        Возвращает участников, отсортированных по стартовой позиции.
        
        Returns:
            Список участников, отсортированных по start_position
        """
        data = self.get_data()
        return sorted(data, key=lambda x: x['start_position'])
    
    def get_participants_sorted_by_lap(self, lap_number: int) -> List[Dict[str, Any]]:
        """
        Возвращает участников, отсортированных по позиции на указанном круге.
        
        Args:
            lap_number: Номер круга (1-12)
        
        Returns:
            Список участников, отсортированных по позиции на круге
        """
        if lap_number < 1 or lap_number > 12:
            raise ValueError("Номер круга должен быть от 1 до 12")
        
        data = self.get_data()
        lap_key = f"lap{lap_number}"
        
        # Фильтруем участников, у которых есть данные для этого круга
        participants_with_lap = [
            p for p in data 
            if lap_key in p and isinstance(p[lap_key], int)
        ]
        
        # Сортируем по позиции на круге
        return sorted(participants_with_lap, key=lambda x: x[lap_key])

