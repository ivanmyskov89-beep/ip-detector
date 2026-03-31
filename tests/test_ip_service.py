import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import Mock, patch
from ip_detector.core.ip_service import IPService
from ip_detector.core.exceptions import APIConnectionError


class TestIPService:
    @patch('ip_detector.core.ip_service.requests.get')
    def test_get_public_ip_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'ip': '1.2.3.4'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        service = IPService()
        ip = service.get_public_ip()
        
        assert ip == '1.2.3.4'
    
    @patch('ip_detector.core.ip_service.requests.get')
    def test_get_public_ip_failure(self, mock_get):
        # Мокируем ConnectionError
        mock_get.side_effect = ConnectionError("No internet")
        
        service = IPService()
        # Ожидаем APIConnectionError (наше кастомное исключение)
        with pytest.raises(APIConnectionError):
            service.get_public_ip()
    
    @patch('ip_detector.core.ip_service.requests.get')
    def test_get_geo_info_success(self, mock_get):
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
    
    @patch('ip_detector.core.ip_service.requests.get')
    def test_get_geo_info_failure(self, mock_get):
        # Мокируем ошибку подключения
        mock_get.side_effect = ConnectionError("Connection failed")
        
        service = IPService()
        with pytest.raises(APIConnectionError):
            service.get_geo_info('1.2.3.4')
