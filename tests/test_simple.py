"""
Простые интеграционные тесты для IP Detector.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


class TestBasicFunctionality:
    """Базовые тесты функциональности."""
    
    def test_import_ip_service(self):
        """Проверка импорта IPService."""
        from ip_detector.core.ip_service import IPService
        assert IPService is not None
    
    def test_import_yadisk_service(self):
        """Проверка импорта YaDiskService."""
        from ip_detector.core.yadisk_service import YaDiskService
        assert YaDiskService is not None
    
    def test_import_exceptions(self):
        """Проверка импорта исключений."""
        from ip_detector.core.exceptions import (
            IPDetectorError, APIConnectionError, TokenError
        )
        assert IPDetectorError is not None
        assert APIConnectionError is not None
        assert TokenError is not None
    
    def test_config_exists(self):
        """Проверка наличия конфигурации."""
        from config import config
        assert config is not None
    
    def test_cli_module_exists(self):
        """Проверка наличия CLI модуля."""
        import cli
        assert cli is not None


class TestIPServiceReal:
    """Реальные тесты IPService (требуют интернет)."""
    
    def test_get_public_ip_real(self):
        """Реальный тест получения IP (требует интернет)."""
        from ip_detector.core.ip_service import IPService
        service = IPService()
        ip = service.get_public_ip()
        assert ip is not None
        assert '.' in ip or ':' in ip  # IPv4 или IPv6
    
    def test_get_geo_info_real(self):
        """Реальный тест получения геолокации (требует интернет)."""
        from ip_detector.core.ip_service import IPService
        service = IPService()
        # Получаем реальный IP
        ip = service.get_public_ip()
        # Получаем геолокацию
        geo = service.get_geo_info(ip)
        assert geo is not None
        assert 'city' in geo or 'country' in geo


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
