import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from services_common.dto import SettingsDTO, FileStatDTO, UnitForTSMScanDTO
from services_common.program_log import ProgramLog
from services_win_service.send_backup_data_to_server import SendBackupDataToServer
from services_win_service.send_backup_tsm_log_data_to_server import SendBackupTSMLogDataToServer
from services_win_service.service_logger import ServiceLogger

LOGGER = ServiceLogger().get_logger()


class FolderScanner:
    """ Предназначен для сканирования папок из преданного списка на предмет новых данных в этих папках."""

    def __init__(self, settings: SettingsDTO):
        self.app_settings: SettingsDTO = settings
        self.backup_endpoint_url = os.path.join(settings.api_endpoint_url, 'backups/')
        # Все найденные при сканировании файлы, которые подходят для вынесения решения на отправку в парсинг
        # self.finding_files: List[FileStatDTO] = []

    def __get_true_file_format(self, file_format_tuple: Tuple[str, ...]) -> Tuple[str, ...]:
        """ Если формат файла не содержит точку в начале, то дополнит точкой и вернет отформатированный кортеж.
         Также если формат установит в нижний регистр."""
        return tuple(
            file_format.lower() if file_format[0] == '.' else '.' + file_format.lower()
            for file_format in file_format_tuple
        )

    def file_format_to_lowercase(self, filename_list: List[str]) -> List[str]:
        """ Вернет список с именами файлов с форматом в нижнем регистре."""
        new_list = []
        for filename in filename_list:
            split_filename = filename.split('.')
            split_filename[-1] = split_filename[-1].lower()
            new_list.append('.'.join(split_filename))
        return new_list

    def get_patterned_files(self, filename_list: List[str], regular_expression: re) -> List[str]:
        """ Предназначен для получения списка файлов исходя из данных по путям и шаблонам названия файла. """
        # print(f"{filename_list=}")
        try:
            return [item for item in filename_list if re.fullmatch(regular_expression, os.path.splitext(item)[0])]
        except Exception:
            return []

    def __get_file_stat_dto(self, file_path: Path) -> FileStatDTO:
        """ Получит необходимую статистику о файле и вернет ее в списке """
        # stat_info.st_atime: Время последнего доступа, выраженное в секундах. (access)
        # stat_info.st_mtime: Время последней модификации контента, выраженное в секундах. (modify)
        # stat_info.st_ctime: Время создания в Windows, выраженное в секундах. (create)
        file_stat = file_path.stat()
        return FileStatDTO(
            file_path=file_path,
            file_size=file_stat.st_size,
            last_access_time=datetime.fromtimestamp(file_stat.st_atime),
            last_modify_time=datetime.fromtimestamp(file_stat.st_mtime),
            last_create_time=datetime.fromtimestamp(file_stat.st_ctime)
        )

    def scan_folders_job(self):
        """ Просканирует все директории из настроек и получит все файлы, которые не директории
        и формат у которых сходится с шаблоном. """

        # Обработаем папки с файлами бэкапов
        for item in self.app_settings.backup_folders:
            try:
                # Проверим, что папка для сканирования вообще существует
                is_exists_folder = item.folder_path.resolve().exists()

                if not is_exists_folder:
                    LOGGER.error(f"Папка {item.folder_path.resolve()} не существует на данном компьютере.")
                else:
                    prepared_finding_files = []
                    # Если * то это значит все файлы из папки
                    if item.allowed_file_formats[0] == "*" and len(item.allowed_file_formats) == 1:
                        finding_files_part = [
                            item.folder_path / filename
                            for filename in self.get_patterned_files(
                                self.file_format_to_lowercase(os.listdir(item.folder_path)),
                                item.reqexp_pattern
                            )
                            if not os.path.isdir(os.path.join(item.folder_path, filename))
                        ]
                    else:
                        finding_files_part = [
                            item.folder_path / filename
                            for filename in self.get_patterned_files(
                                self.file_format_to_lowercase(os.listdir(item.folder_path)),
                                item.reqexp_pattern
                            )
                            if not os.path.isdir(os.path.join(item.folder_path, filename)) and filename.endswith(
                                self.__get_true_file_format(item.allowed_file_formats)
                            )
                        ]
                    prepared_finding_files += [
                        self.__get_file_stat_dto(item)
                        for item in finding_files_part
                    ]

                    # Отправим данные на сервер-наблюдатель
                    SendBackupDataToServer(
                        settings=self.app_settings,
                        server_data=item,
                        prepared_files=prepared_finding_files
                    )
            except PermissionError:
                ProgramLog(
                    logger=LOGGER,
                    current_message=f"PermissionError. Нет доступа к папке {str(item.folder_path)} на данном компьютере."
                ).error_program_log()

        # Обработаем TSM файлы с логами
        for tsl_log_file_item in self.app_settings.backup_tsm_log_files:
            tsl_log_file_item: UnitForTSMScanDTO = tsl_log_file_item
            with tsl_log_file_item.path_to_log_file.open(
                    mode='r'
                    # ,encoding=get_file_encoding(tsl_log_file_item.path_to_log_file)
            ) as fd:
                revert_tail_file_data_list = [item.strip() for item in fd.readlines()[-20:] if bool(item.strip())][::-1]
                buffer = []
                separator_line_count = 0
                for item in revert_tail_file_data_list:
                    if item == '----------------------------------------------------------------------':
                        separator_line_count += 1
                    buffer.append(item)
                    if separator_line_count == 2:
                        break
                # print(f"{buffer[::-1]=}")

                # Отправим данные на сервер-наблюдатель
                SendBackupTSMLogDataToServer(
                    settings=self.app_settings,
                    server_data=tsl_log_file_item,
                    last_backup_log=buffer[::-1]
                )

    if __name__ == '__main__':
        print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
