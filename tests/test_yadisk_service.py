import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import Mock, patch
from ip_detector.core.yadisk_service import YaDiskService
from ip_detector.core.exceptions import TokenError, APIConnectionError


class TestYaDiskService:
    def test_init_without_token(self):
        with patch('ip_detector.core.yadisk_service.config') as mock_config:
            mock_config.YA_TOKEN = ''
            with pytest.raises(TokenError):
                YaDiskService(token='')
    
    @patch('ip_detector.core.yadisk_service.requests.get')
    def test_check_connection_success(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        service = YaDiskService(token='test_token')
        assert service.check_connection() is True
    
    @patch('ip_detector.core.yadisk_service.requests.get')
    def test_check_connection_failure(self, mock_get):
        # Мокируем ошибку подключения
        mock_get.side_effect = Exception("Connection error")
        
        service = YaDiskService(token='test_token')
        # check_connection возвращает False при ошибке, а не выбрасывает исключение
        assert service.check_connection() is False
    
    @patch('ip_detector.core.yadisk_service.requests.put')
    @patch('ip_detector.core.yadisk_service.requests.get')
    def test_create_folder_success(self, mock_get, mock_put):
        # Мок для проверки подключения
        mock_response_get = Mock()
        mock_response_get.raise_for_status = Mock()
        mock_get.return_value = mock_response_get
        
        # Мок для создания папки
        mock_response_put = Mock()
        mock_response_put.status_code = 201
        mock_put.return_value = mock_response_put
        
        service = YaDiskService(token='test_token')
        result = service.create_folder("TestFolder")
        
        assert result is True
