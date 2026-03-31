"""
Модуль для работы с REST API Яндекс.Диска.
Улучшенная версия с логированием и обработкой ошибок.
"""
import os
from typing import Optional
import requests
from loguru import logger
from config import config
from ip_detector.core.exceptions import APIConnectionError, TokenError, FileOperationError


class YaDiskService:
    """Класс для загрузки файлов на Яндекс.Диск."""

    BASE_URL = "https://cloud-api.yandex.net/v1/disk"

    def __init__(self, token: Optional[str] = None):
        """
        Инициализация сервиса Яндекс.Диска.

        Args:
            token: OAuth-токен для доступа к Яндекс.Диску.
        """
        self.token = token or config.YA_TOKEN
        
        if not self.token:
            raise TokenError("Токен Яндекс.Диска не указан")
        
        self.headers = {
            "Authorization": f"OAuth {self.token}",
            "Content-Type": "application/json"
        }
        logger.info("YaDiskService инициализирован")

    def check_connection(self) -> bool:
        """
        Проверка подключения к Яндекс.Диску.

        Returns:
            bool: True если подключение успешно.
        """
        url = f"{self.BASE_URL}/"
        logger.debug("Проверка подключения к Яндекс.Диску")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.success("Подключение к Яндекс.Диску успешно")
            return True
        except requests.RequestException as e:
            logger.error(f"Ошибка подключения: {e}")
            return False

    def create_folder(self, folder_path: str) -> bool:
        """
        Создание папки на Яндекс.Диске.

        Args:
            folder_path: Путь к папке (относительный).

        Returns:
            bool: True если папка создана или уже существует.
        """
        url = f"{self.BASE_URL}/resources"
        params = {"path": folder_path}
        logger.info(f"Создание папки: {folder_path}")

        try:
            response = requests.put(url, headers=self.headers, params=params, timeout=30)

            if response.status_code == 201:
                logger.success(f"Папка создана: {folder_path}")
                return True
            elif response.status_code == 409:
                logger.info(f"Папка уже существует: {folder_path}")
                return True
            else:
                response.raise_for_status()
                return False
        except requests.RequestException as e:
            logger.error(f"Ошибка создания папки: {e}")
            raise APIConnectionError(f"Не удалось создать папку: {e}")

    def upload_file(self, local_file_path: str, remote_folder: Optional[str] = None) -> bool:
        """
        Загрузка файла на Яндекс.Диск.

        Args:
            local_file_path: Путь к локальному файлу.
            remote_folder: Имя папки на Яндекс.Диске.

        Returns:
            bool: True если загрузка успешна.
        """
        remote_folder = remote_folder or config.DEFAULT_FOLDER_NAME
        
        if not os.path.exists(local_file_path):
            raise FileOperationError(f"Файл {local_file_path} не найден")

        remote_path = f"{remote_folder}/{os.path.basename(local_file_path)}"
        logger.info(f"Загрузка файла: {local_file_path} -> {remote_path}")

        # Создаём папку
        self.create_folder(remote_folder)

        # Получаем ссылку для загрузки
        upload_url = self._get_upload_link(remote_path)
        
        if not upload_url:
            raise APIConnectionError("Не удалось получить ссылку для загрузки")

        # Загружаем файл
        try:
            with open(local_file_path, 'rb') as f:
                response = requests.put(upload_url, data=f, timeout=60)
                response.raise_for_status()
            logger.success(f"Файл загружен: {remote_path}")
            return True
        except requests.RequestException as e:
            logger.error(f"Ошибка загрузки: {e}")
            raise APIConnectionError(f"Не удалось загрузить файл: {e}")

    def _get_upload_link(self, file_path: str) -> Optional[str]:
        """
        Получение ссылки для загрузки файла.

        Args:
            file_path: Путь к файлу на Яндекс.Диске.

        Returns:
            Optional[str]: Ссылка для загрузки или None.
        """
        url = f"{self.BASE_URL}/resources/upload"
        params = {"path": file_path, "overwrite": True}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json().get("href")
        except requests.RequestException as e:
            logger.error(f"Ошибка получения ссылки: {e}")
            return None
