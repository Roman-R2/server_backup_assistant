import logging
from pathlib import Path


class Settings:
    """ Содержит настройки для работы скрипта. """
    BASE_DIR = Path(__file__).resolve().parent.parent

    OS_ENVIRON_TZ = 'RTZ-05'

    # -------------- Общие настройки
    # SETTINGS_FILE = BASE_DIR / 'data' / 'settings.yaml'
    # Общая кодировка проекта
    COMMON_ENCODING = 'utf-8'
    # папка с катринками для GUI
    GUI_IMAGE_FOLDER = BASE_DIR / 'assets' / 'images'

    # -------------- Настройки, связанные с системой авторизации
    # TOKEN_FILE = BASE_DIR / 'data' / '.token'

    # --------------  Настройки логирования
    # Общий уровень логирования
    LOGGING_LEVEL = logging.DEBUG
    # Имя логера для записи логов GUI
    GUI_LOGGER_NAME = 'gui_event_logger'
    # Имя логера для записи логов windows service
    SERVICE_LOGGER_NAME = 'gui_event_logger'
    # Папка логов для GUI
    GUI_LOG_FOLDER = BASE_DIR / 'logs' / 'server_assistant_gui_logs'
    # Папка логов для windows service
    SERVICE_LOG_FOLDER = BASE_DIR / 'logs' / 'server_assistant_windows_service_logs'
    # Файлы логов
    GUI_LOG_FILE = GUI_LOG_FOLDER / 'gui_assistant.log'
    SERVICE_LOG_FILE = SERVICE_LOG_FOLDER / 'service_assistant.log'

    # --------------  Настройки БД
    SQLITE3_DATABASE_FILE = BASE_DIR / 'db' / 'assistant.sqlite3'

    # --------------  Файл с URI до IPI сервера-наблюдателя по умолчанию
    DEFAULT_API_ENDPOINT_FILE = BASE_DIR / 'data' / 'default_server_url.txt'


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
