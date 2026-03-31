"""
Модуль для работы с REST API Яндекс.Диска.
"""
import os
from typing import Optional
import requests


class YaDiskService:
    """Класс для загрузки файлов на Яндекс.Диск."""

    BASE_URL = "https://cloud-api.yandex.net/v1/disk"

    def __init__(self, token: str):
        """
        Инициализация сервиса Яндекс.Диска.

        Args:
            token: OAuth-токен для доступа к Яндекс.Диску.
        """
        self.token = token
        self.headers = {
            "Authorization": f"OAuth {token}",
            "Content-Type": "application/json"
        }

    def create_folder(self, folder_path: str) -> bool:
        """
        Создание папки на Яндекс.Диске.

        Args:
            folder_path: Путь к папке (относительный).

        Returns:
            bool: True если папка создана или уже существует.

        Raises:
            Exception: Если не удалось создать папку.
        """
        url = f"{self.BASE_URL}/resources"
        params = {"path": folder_path}

        try:
            response = requests.put(url, headers=self.headers,
                                    params=params, timeout=30)

            if response.status_code == 201:
                return True
            elif response.status_code == 409:
                return True
            else:
                response.raise_for_status()
                return False
        except requests.RequestException as e:
            raise Exception(f"Ошибка создания папки: {e}")

    def get_upload_link(self, file_path: str) -> Optional[str]:
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
            response = requests.get(url, headers=self.headers,
                                    params=params, timeout=30)
            response.raise_for_status()
            return response.json().get("href")
        except requests.RequestException as e:
            raise Exception(f"Ошибка получения ссылки для загрузки: {e}")

    def upload_file(self, local_file_path: str,
                    remote_folder: str = "IP_Detector") -> bool:
        """
        Загрузка файла на Яндекс.Диск.

        Args:
            local_file_path: Путь к локальному файлу.
            remote_folder: Имя папки на Яндекс.Диске.

        Returns:
            bool: True если загрузка успешна.

        Raises:
            Exception: Если не удалось загрузить файл.
        """
        if not os.path.exists(local_file_path):
            raise Exception(f"Файл {local_file_path} не найден")

        remote_path = f"{remote_folder}/{os.path.basename(local_file_path)}"

        self.create_folder(remote_folder)

        upload_url = self.get_upload_link(remote_path)

        if not upload_url:
            raise Exception("Не удалось получить ссылку для загрузки")

        try:
            with open(local_file_path, 'rb') as f:
                response = requests.put(upload_url, data=f, timeout=60)
                response.raise_for_status()
            return True
        except requests.RequestException as e:
            raise Exception(f"Ошибка загрузки файла: {e}")

    def check_connection(self) -> bool:
        """
        Проверка подключения к Яндекс.Диску.

        Returns:
            bool: True если подключение успешно.
        """
        url = f"{self.BASE_URL}/"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False
