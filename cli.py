"""
Интерфейс командной строки для IP Detector.
"""
import sys
import click
from loguru import logger
from ip_detector.core.ip_service import IPService
from ip_detector.core.yadisk_service import YaDiskService
from config import config


@click.command()
@click.option('--output', '-o', default=None, help='Имя выходного JSON файла')
@click.option('--folder', '-f', default=None, help='Папка на Яндекс.Диске')
@click.option('--verbose', '-v', is_flag=True, help='Подробный вывод')
@click.option('--no-upload', is_flag=True, help='Не загружать на Яндекс.Диск')
@click.option('--keep-file', is_flag=True, help='Не удалять локальный файл')
def main(output, folder, verbose, no_upload, keep_file):
    """IP Detector - Определение геолокации по IP-адресу."""
    
    # Настройка логирования
    if verbose:
        logger.add(sys.stdout, level="DEBUG")
    else:
        logger.add(sys.stdout, level="INFO")
    
    click.echo("=" * 50)
    click.echo("IP Detector v2.0 - Определение геолокации по IP")
    click.echo("=" * 50)
    
    try:
        # Проверка конфигурации
        config.validate()
        
        # Получение IP
        click.echo("\n[1/4] Определение IP-адреса...")
        ip_service = IPService()
        current_ip = ip_service.get_public_ip()
        click.secho(f"       ✓ Ваш IP-адрес: {current_ip}", fg='green')
        
        # Получение геолокации
        click.echo("\n[2/4] Получение геолокации по IP...")
        geo_info = ip_service.get_geo_info(current_ip)
        
        city = geo_info.get('city', 'Неизвестно')
        country = geo_info.get('country', 'Неизвестно')
        location = geo_info.get('loc', 'Неизвестно')
        
        click.secho(f"       ✓ Город: {city}", fg='green')
        click.secho(f"       ✓ Страна: {country}", fg='green')
        click.secho(f"       ✓ Координаты: {location}", fg='green')
        
        # Сохранение в JSON
        output_file = output or config.DEFAULT_OUTPUT_FILE
        click.echo(f"\n[3/4] Сохранение данных в файл {output_file}...")
        saved_file = ip_service.save_to_json(output_file)
        click.secho(f"       ✓ Файл сохранён: {saved_file}", fg='green')
        
        # Загрузка на Яндекс.Диск
        if not no_upload:
            click.echo("\n[4/4] Загрузка файла на Яндекс.Диск...")
            yadisk = YaDiskService()
            
            if not yadisk.check_connection():
                raise Exception("Не удалось подключиться к Яндекс.Диску")
            
            remote_folder = folder or config.DEFAULT_FOLDER_NAME
            yadisk.upload_file(saved_file, remote_folder)
            click.secho(f"       ✓ Файл загружен в папку '{remote_folder}'", fg='green')
        else:
            click.echo("\n[4/4] Пропуск загрузки на Яндекс.Диск")
        
        # Очистка
        if not keep_file and not no_upload:
            import os
            if os.path.exists(saved_file):
                os.remove(saved_file)
                click.echo(f"\n[Очистка] Локальный файл {saved_file} удалён")
        
        click.echo("\n" + "=" * 50)
        click.secho("✅ Программа выполнена успешно!", fg='green', bold=True)
        click.echo("=" * 50)
        
    except Exception as e:
        click.secho(f"\n❌ Ошибка: {e}", fg='red', err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
