from datetime import datetime
from pathlib import Path
from typing import List, NamedTuple, Tuple
from urllib.parse import urlparse


class UnitForScanDTO(NamedTuple):
    """ DTO содержит информацию необходимую для сканирования папок на предмет новых файлов для парсинга данных."""
    # Путь до папки, в которой находятся файлы для сканирования
    folder_path: Path
    # # Идентификатор сервера в таблице серверов для наблюдения на стороне сервера-наблюдателя
    # server_id: int
    # Шаблон для регулярного выражения я прямого сопоставления с именен файла
    reqexp_pattern: str
    # Кортеж, содержащий форматы файлов для сканирования в виде строки (регистр, верхний или нижний, не важен)
    allowed_file_formats: Tuple[str, ...]


class UnitForTSMScanDTO(NamedTuple):
    """ DTO содержит информацию необходимую для сканирования файлов-логов от TSM."""
    # Наименование для БД, по которой производится бэкап
    log_file_name: str
    # Путь до файла лога с информацией о ходе бэкапа
    path_to_log_file: Path


class SettingsDTO(NamedTuple):
    """ DTO содержит информацию о настройках фсистента по наблюдению за бэкапами."""
    # Ресурс на который нужно отправлять данные
    api_endpoint_url: urlparse
    # Логин для авторизации на стороне сервера
    api_login: str
    # Пароль для авторизации на стороне сервера
    api_password: str
    # # Id сервера для данных статистики в  системе наблюдателя
    # server_stat_id_from_server_watcher: int
    # Периодичность отправки статистики о бэкапах (в минутах)
    backup_sending_minutes_frequency: int
    # Периодичность отправки статистики о железе и программах (в минутах)
    stat_sending_minutes_frequency: int
    # Периодичность отправки сигнала присутствия (в минутах)
    precision_sending_minutes_frequency: int
    # Периодичность отправки запроса настроек (в минутах)
    ask_settings_minutes_frequency: int
    # Папки для сканирования бэкапов в них
    backup_folders: List[UnitForScanDTO]
    # Фалы логов TSM для сканирования бэкапов в них
    backup_tsm_log_files: List[UnitForTSMScanDTO]


class FileStatDTO(NamedTuple):
    # Полный путь до файла
    file_path: Path
    # Размер файла в байтах
    file_size: int
    # Время последнего доступа. (access)
    last_access_time: datetime
    # Время последней модификации контента. (modify)
    last_modify_time: datetime
    # Время создания. (create)
    last_create_time: datetime


class PhysicalMemoryDTO(NamedTuple):
    """ ДТО для передачи данных памяти. """
    # Общая физическая память (без файла подкачки)
    total: int
    # Доступная памяь
    available: int
    # Процент используемой памяти
    percent: float
    # Используемая память
    used: int
    # Свободная память (память которая не используется вообще, которая обнуляется)
    free: int


class SwapMemoryDTO(NamedTuple):
    """ ДТО для передачи данных памяти файла подкачки. """
    # sswap(total=2550136832, used=1132179456, free=1417957376, percent=44.4, sin=0, sout=0)
    # Общая память
    total: int
    # Используемая памяь
    used: int
    # Свободная память
    free: int
    # Процент используемой памяти
    percent: float


class PhysicalDiskDTO(NamedTuple):
    """ ДТО для передачи данных физического диска хранения данных. """
    # Метка устройства
    device: str
    # Точка монитрования
    mountpoint: str
    # Тип файловой системы
    fstype: str
    opts: str
    maxfile: int
    maxpath: int
    # Всего места
    total: int
    # Используется места
    used: int
    # Спободно места
    free: int
    # используется места в процентах
    percent: float


class InstalledProgramDTO(NamedTuple):
    """ ДТО для передачи данных об установленной программе. """
    # Имя программы
    display_name: str
    # Версия программы
    display_version: str
    # Папка в которую установлена программа
    install_location: str


class ServerStatDTO(NamedTuple):
    """ ДТО для предачи данных статистики сервера по железу. """
    token: str
    platform: str
    platform_release: str
    platform_version: str
    architecture: str
    hostname: str
    ip_address: str
    mac_address: str
    processor: str
    physical_memory: List[PhysicalMemoryDTO]
    swap_memory: List[SwapMemoryDTO]
    disks: List[PhysicalDiskDTO]
    installed_programs: List[InstalledProgramDTO]


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
