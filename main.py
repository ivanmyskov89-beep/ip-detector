"""
Главный модуль программы IP Detector.
Определяет IP, получает геолокацию, сохраняет в JSON и загружает на Яндекс.Диск.
"""
import os
import sys
from ip_service import IPService
from yadisk_service import YaDiskService


def main():
    """
    Основная функция программы.
    """
    print("=" * 50)
    print("IP Detector - Определение геолокации по IP")
    print("=" * 50)

    # Токен Яндекс.Диска (получен из полигона)
    YA_TOKEN = "y0__xDU25-SBxjblgMg4ff69hYw992b3QdIa2UGl_v32Fik1rH4Ve9ddWPPaA"

    json_filename = "ip_info.json"

    try:
        # Шаг 1: Получение IP
        print("\n[1/4] Определение IP-адреса...")
        ip_service = IPService()
        current_ip = ip_service.get_public_ip()
        print(f"       Ваш IP-адрес: {current_ip}")

        # Шаг 2: Получение геолокации
        print("\n[2/4] Получение геолокации по IP...")
        geo_info = ip_service.get_geo_info(current_ip)

        city = geo_info.get('city', 'Неизвестно')
        country = geo_info.get('country', 'Неизвестно')
        location = geo_info.get('loc', 'Неизвестно')
        print(f"       Город: {city}")
        print(f"       Страна: {country}")
        print(f"       Координаты: {location}")

        # Шаг 3: Сохранение в JSON
        print(f"\n[3/4] Сохранение данных в файл {json_filename}...")
        saved_file = ip_service.save_to_json(json_filename)
        print(f"       Файл сохранён: {saved_file}")

        # Шаг 4: Загрузка на Яндекс.Диск
        print("\n[4/4] Загрузка файла на Яндекс.Диск...")
        yadisk = YaDiskService(YA_TOKEN)

        if not yadisk.check_connection():
            raise Exception("Не удалось подключиться к Яндекс.Диску")

        upload_success = yadisk.upload_file(saved_file, "IP_Detector")
        if upload_success:
            print("       Файл успешно загружен в папку 'IP_Detector'")

        print("\n" + "=" * 50)
        print("✅ Программа выполнена успешно!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    finally:
        # Удаление локального JSON-файла (чтобы не оставалось лишних файлов)
        if os.path.exists(json_filename):
            try:
                os.remove(json_filename)
                print(f"\n[Очистка] Локальный файл {json_filename} удалён")
            except OSError:
                pass


if __name__ == "__main__":
    main()
