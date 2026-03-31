"""
Тесты для YaDiskService.
"""
import pytest
from unittest.mock import Mock, patch, mock_open
from ip_detector.core.yadisk_service import YaDiskService
from ip_detector.core.exceptions import TokenError


class TestYaDiskService:
    """Тесты для YaDiskService."""
    
    def test_init_without_token(self):
        """Тест инициализации без токена."""
        with patch('ip_detector.core.yadisk_service.config') as mock_config:
            mock_config.YA_TOKEN = ''
            with pytest.raises(TokenError):
                YaDiskService(token='')
    
    @patch('ip_detector.core.yadisk_service.requests.get')
    def test_check_connection_success(self, mock_get):
        """Тест успешной проверки подключения."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        service = YaDiskService(token='test_token')
        assert service.check_connection() is True
    
    @patch('ip_detector.core.yadisk_service.requests.get')
    def test_check_connection_failure(self, mock_get):
        """Тест неудачной проверки подключения."""
        mock_get.side_effect = Exception("Connection error")
        
        service = YaDiskService(token='test_token')
        assert service.check_connection() is False
