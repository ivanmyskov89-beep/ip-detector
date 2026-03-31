"""
Конфигурация приложения.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

class Config:
    """Класс конфигурации."""
    
    # Яндекс.Диск
    YA_TOKEN = os.getenv('YA_TOKEN', '')
    
    # API endpoints
    IPIFY_URL = os.getenv('IPIFY_URL', 'https://api.ipify.org')
    IPINFO_URL = os.getenv('IPINFO_URL', 'https://ipinfo.io')
    
    # Настройки
    DEFAULT_OUTPUT_FILE = os.getenv('DEFAULT_OUTPUT_FILE', 'ip_info.json')
    DEFAULT_FOLDER_NAME = os.getenv('DEFAULT_FOLDER_NAME', 'IP_Detector')
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Настройки веб-сервера
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Пути
    BASE_DIR = Path(__file__).parent
    LOGS_DIR = BASE_DIR / 'logs'
    
    @classmethod
    def validate(cls):
        """Проверка обязательных настроек."""
        if not cls.YA_TOKEN:
            raise ValueError("YA_TOKEN не установлен в .env файле")
        return True

config = Config()
