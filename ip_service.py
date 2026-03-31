"""
Модуль для работы с сервисами определения IP и геолокации.
"""
import json
from datetime import datetime
from typing import Dict, Any
import requests


class IPService:
    """Класс для получения IP-адреса и геолокации через внешние API."""

    IPIFY_API_URL = "https://api.ipify.org?format=json"
    IPINFO_API_URL = "https://ipinfo.io/{ip}/geo"

    def __init__(self):
        """Инициализация сервиса."""
        self.current_ip = None
        self.geo_info = None

    def get_public_ip(self) -> str:
        """
        Получение публичного IP-адреса через сервис ipify.

        Returns:
            str: IP-адрес пользователя.

        Raises:
            Exception: Если не удалось получить IP-адрес.
        """
        try:
            response = requests.get(self.IPIFY_API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.current_ip = data.get("ip")
            return self.current_ip
        except requests.RequestException as e:
            raise Exception(f"Ошибка получения IP-адреса: {e}")

    def get_geo_info(self, ip_address: str) -> Dict[str, Any]:
        """
        Получение геолокации по IP через сервис ipinfo.

        Args:
            ip_address: IP-адрес для геолокации.

        Returns:
            Dict[str, Any]: Словарь с геоданными.

        Raises:
            Exception: Если не удалось получить геоинформацию.
        """
        try:
            url = self.IPINFO_API_URL.format(ip=ip_address)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            self.geo_info = response.json()
            return self.geo_info
        except requests.RequestException as e:
            raise Exception(f"Ошибка получения геоинформации: {e}")

    def save_to_json(self, filename: str = "ip_info.json") -> str:
        """
        Сохранение IP и геоинформации в JSON файл.

        Args:
            filename: Имя файла для сохранения.

        Returns:
            str: Путь к сохранённому файлу.

        Raises:
            Exception: Если данные не получены или не удалось сохранить файл.
        """
        if not self.current_ip or not self.geo_info:
            raise Exception("Нет данных для сохранения. "
                            "Сначала получите IP и геоинформацию.")

        data_to_save = {
            "timestamp": datetime.now().isoformat(),
            "ip": self.current_ip,
            "geo": self.geo_info
        }

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
            return filename
        except IOError as e:
            raise Exception(f"Ошибка сохранения файла: {e}")
