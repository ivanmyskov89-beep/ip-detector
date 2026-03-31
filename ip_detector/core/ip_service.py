"""
Модуль для работы с сервисами определения IP и геолокации.
Улучшенная версия с логированием и обработкой ошибок.
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from loguru import logger
from config import config
from ip_detector.core.exceptions import APIConnectionError, APIResponseError, FileOperationError


class IPService:
    """Класс для получения IP-адреса и геолокации через внешние API."""

    def __init__(self):
        """Инициализация сервиса."""
        self.current_ip = None
        self.geo_info = None
        logger.info("IPService инициализирован")

    def get_public_ip(self) -> str:
        """
        Получение публичного IP-адреса через сервис ipify.

        Returns:
            str: IP-адрес пользователя.

        Raises:
            APIConnectionError: Если не удалось подключиться к API.
            APIResponseError: Если API вернул ошибку.
        """
        logger.info(f"Запрос IP-адреса через {config.IPIFY_URL}")
        
        try:
            response = requests.get(
                config.IPIFY_URL,
                params={'format': 'json'},
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            self.current_ip = data.get("ip")
            
            if not self.current_ip:
                raise APIResponseError("API не вернул IP-адрес")
            
            logger.success(f"IP-адрес получен: {self.current_ip}")
            return self.current_ip
            
        except requests.ConnectionError as e:
            logger.error(f"Ошибка подключения: {e}")
            raise APIConnectionError(f"Не удалось подключиться к {config.IPIFY_URL}")
        except requests.Timeout as e:
            logger.error(f"Таймаут подключения: {e}")
            raise APIConnectionError(f"Превышен таймаут подключения к API")
        except requests.RequestException as e:
            logger.error(f"Ошибка API: {e}")
            raise APIResponseError(f"API вернул ошибку: {e}")

    def get_geo_info(self, ip_address: str) -> Dict[str, Any]:
        """
        Получение геолокации по IP через сервис ipinfo.

        Args:
            ip_address: IP-адрес для геолокации.

        Returns:
            Dict[str, Any]: Словарь с геоданными.

        Raises:
            APIConnectionError: Если не удалось подключиться к API.
            APIResponseError: Если API вернул ошибку.
        """
        url = f"{config.IPINFO_URL}/{ip_address}/geo"
        logger.info(f"Запрос геолокации для {ip_address}")
        
        try:
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            self.geo_info = response.json()
            
            logger.success(f"Геоданные получены: {self.geo_info.get('city', 'Unknown')}")
            return self.geo_info
            
        except requests.ConnectionError as e:
            logger.error(f"Ошибка подключения: {e}")
            raise APIConnectionError(f"Не удалось подключиться к {config.IPINFO_URL}")
        except requests.Timeout as e:
            logger.error(f"Таймаут подключения: {e}")
            raise APIConnectionError(f"Превышен таймаут подключения к API")
        except requests.RequestException as e:
            logger.error(f"Ошибка API: {e}")
            raise APIResponseError(f"API вернул ошибку: {e}")

    def save_to_json(self, filename: Optional[str] = None) -> str:
        """
        Сохранение IP и геоинформации в JSON файл.

        Args:
            filename: Имя файла для сохранения.

        Returns:
            str: Путь к сохранённому файлу.

        Raises:
            FileOperationError: Если данные не получены или не удалось сохранить файл.
        """
        if not self.current_ip or not self.geo_info:
            raise FileOperationError("Нет данных для сохранения")
        
        filename = filename or config.DEFAULT_OUTPUT_FILE
        
        data_to_save = {
            "timestamp": datetime.now().isoformat(),
            "ip": self.current_ip,
            "geo": self.geo_info
        }
        
        logger.info(f"Сохранение данных в {filename}")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
            logger.success(f"Файл сохранён: {filename}")
            return filename
        except IOError as e:
            logger.error(f"Ошибка сохранения: {e}")
            raise FileOperationError(f"Не удалось сохранить файл: {e}")
