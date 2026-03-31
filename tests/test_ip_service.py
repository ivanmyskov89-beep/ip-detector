"""
Тесты для IPService.
"""
import pytest
from unittest.mock import Mock, patch
from ip_detector.core.ip_service import IPService
from ip_detector.core.exceptions import APIConnectionError, APIResponseError


class TestIPService:
    """Тесты для IPService."""
    
    @patch('ip_detector.core.ip_service.requests.get')
    def test_get_public_ip_success(self, mock_get):
        """Тест успешного получения IP."""
        mock_response = Mock()
        mock_response.json.return_value = {'ip': '1.2.3.4'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        service = IPService()
        ip = service.get_public_ip()
        
        assert ip == '1.2.3.4'
        assert service.current_ip == '1.2.3.4'
    
    @patch('ip_detector.core.ip_service.requests.get')
    def test_get_public_ip_connection_error(self, mock_get):
        """Тест ошибки подключения."""
        mock_get.side_effect = ConnectionError("No internet")
        
        service = IPService()
        with pytest.raises(APIConnectionError):
            service.get_public_ip()
    
    @patch('ip_detector.core.ip_service.requests.get')
    def test_get_geo_info_success(self, mock_get):
        """Тест успешного получения геолокации."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'city': 'Moscow',
            'country': 'RU',
            'loc': '55.7522,37.6156'
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        service = IPService()
        geo = service.get_geo_info('1.2.3.4')
        
        assert geo['city'] == 'Moscow'
        assert geo['country'] == 'RU'
    
    def test_save_to_json_no_data(self):
        """Тест сохранения без данных."""
        service = IPService()
        with pytest.raises(Exception):
            service.save_to_json()
