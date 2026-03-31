"""
Кастомные исключения для приложения.
"""

class IPDetectorError(Exception):
    """Базовый класс для всех ошибок приложения."""
    pass

class APIConnectionError(IPDetectorError):
    """Ошибка подключения к API."""
    pass

class APIResponseError(IPDetectorError):
    """Ошибка в ответе API."""
    pass

class TokenError(IPDetectorError):
    """Ошибка с токеном Яндекс.Диска."""
    pass

class FileOperationError(IPDetectorError):
    """Ошибка при работе с файлами."""
    pass
