"""
Веб-интерфейс для IP Detector (упрощённая версия).
"""
import sys
import os
from pathlib import Path

# Добавляем родительскую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template_string, jsonify
from loguru import logger
from ip_detector.core.ip_service import IPService
from ip_detector.core.yadisk_service import YaDiskService

app = Flask(__name__)

# HTML шаблон
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IP Detector</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        h1 { color: #333; margin-bottom: 10px; font-size: 2em; }
        .subtitle { color: #666; margin-bottom: 30px; }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            border-radius: 50px;
            cursor: pointer;
            transition: transform 0.2s;
            margin-bottom: 30px;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .result {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            text-align: left;
            display: none;
        }
        .result.show { display: block; animation: slideIn 0.5s ease; }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .info-item {
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
        }
        .info-item:last-child { border-bottom: none; }
        .info-label { font-weight: 600; color: #555; }
        .info-value { color: #333; text-align: right; }
        .success { color: #4caf50; font-weight: bold; margin-bottom: 20px; }
        .error { color: #f44336; font-weight: bold; margin-bottom: 20px; }
        .loader {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .footer { margin-top: 30px; color: #999; font-size: 12px; }
        @media (max-width: 600px) {
            .container { padding: 20px; }
            .info-item { flex-direction: column; }
            .info-value { text-align: left; margin-top: 5px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📍 IP Detector</h1>
        <p class="subtitle">Определение геолокации по IP-адресу</p>
        <button class="btn" id="detectBtn">🔍 Определить моё местоположение</button>
        <div id="result" class="result">
            <div id="status"></div>
            <div id="info"></div>
        </div>
        <div class="footer">Данные загружаются на Яндекс.Диск в папку "IP_Detector"</div>
    </div>
    
    <script>
        const detectBtn = document.getElementById('detectBtn');
        const resultDiv = document.getElementById('result');
        const statusDiv = document.getElementById('status');
        const infoDiv = document.getElementById('info');
        
        detectBtn.addEventListener('click', async () => {
            detectBtn.disabled = true;
            detectBtn.innerHTML = 'Определяем... <span class="loader"></span>';
            resultDiv.classList.remove('show');
            statusDiv.innerHTML = '';
            infoDiv.innerHTML = '';
            
            try {
                const response = await fetch('/api/detect');
                const data = await response.json();
                
                if (data.success) {
                    statusDiv.innerHTML = '<div class="success">✅ Данные успешно загружены на Яндекс.Диск!</div>';
                    infoDiv.innerHTML = `
                        <div class="info-item"><span class="info-label">🌐 IP:</span><span class="info-value">${data.data.ip}</span></div>
                        <div class="info-item"><span class="info-label">🏙️ Город:</span><span class="info-value">${data.data.city}</span></div>
                        <div class="info-item"><span class="info-label">🇷🇺 Страна:</span><span class="info-value">${data.data.country}</span></div>
                        <div class="info-item"><span class="info-label">📍 Координаты:</span><span class="info-value">${data.data.location}</span></div>
                        <div class="info-item"><span class="info-label">⏰ Часовой пояс:</span><span class="info-value">${data.data.timezone}</span></div>
                    `;
                    resultDiv.classList.add('show');
                } else {
                    statusDiv.innerHTML = `<div class="error">❌ ${data.error}</div>`;
                    resultDiv.classList.add('show');
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="error">❌ Ошибка: ${error.message}</div>`;
                resultDiv.classList.add('show');
            } finally {
                detectBtn.disabled = false;
                detectBtn.innerHTML = '🔍 Определить моё местоположение';
            }
        });
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    """Главная страница."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/detect')
def detect_ip():
    """API endpoint для определения IP и геолокации."""
    try:
        # Получаем IP
        ip_service = IPService()
        ip_address = ip_service.get_public_ip()
        
        # Получаем геолокацию
        geo_info = ip_service.get_geo_info(ip_address)
        
        # Сохраняем файл
        filename = ip_service.save_to_json()
        
        # Загружаем на Яндекс.Диск
        yadisk = YaDiskService()
        yadisk.upload_file(filename)
        
        # Удаляем локальный файл
        if os.path.exists(filename):
            os.remove(filename)
        
        return jsonify({
            'success': True,
            'data': {
                'ip': ip_address,
                'city': geo_info.get('city', 'Unknown'),
                'country': geo_info.get('country', 'Unknown'),
                'location': geo_info.get('loc', 'Unknown'),
                'timezone': geo_info.get('timezone', 'Unknown')
            }
        })
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health')
def health():
    """Проверка работоспособности."""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)
    
    print("\n" + "=" * 50)
    print("🌐 IP Detector Web Interface")
    print("=" * 50)
    print("📍 Откройте в браузере: http://localhost:5000")
    print("🛑 Нажмите CTRL+C для остановки")
    print("=" * 50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
