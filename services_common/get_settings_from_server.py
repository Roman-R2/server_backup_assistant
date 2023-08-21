import json
from logging import Logger
from pathlib import Path

import requests

from services_common.common_services import JsonHeaderMixin
from services_common.db_connector import DBConnector
from services_common.dto import UnitForScanDTO, SettingsDTO, UnitForTSMScanDTO
from services_common.http_statuses import Status
from services_common.program_log import ProgramLog
from services_common.server_endpoint import ServerEndpoint


class GetSettingsFromServer(JsonHeaderMixin):
    """ Получит настройки для асистента с сервера-наблюдателя. """

    def __init__(self, logger: Logger):
        super().__init__()
        self.logger = logger
        self.receive_settings_url = ServerEndpoint(logger=self.logger).get_true_endpoint(add_string="get_my_settings")
        authorization_token = DBConnector.get_token()
        self.data = {
            "token": authorization_token
        }
        self.headers['Authorization'] = f'Token {authorization_token}'

    def _launch(self):
        try:
            with requests.post(
                    url=self.receive_settings_url,
                    data=json.dumps(self.data, indent=4, sort_keys=True, default=str),
                    headers=self.headers,
            ) as response:
                if response.status_code != Status.HTTP_200_OK:
                    ProgramLog(logger=self.logger).critical_response_log(
                        response=response,
                        endpoint_url=self.receive_settings_url,
                        headers=self.headers,
                        data=self.data
                    )
                    message = (f"\nНевозможно получить настройки с сервера."
                               f"\nСервер вернул статус {response.status_code}"
                               f"\n{response.json()}\n")
                    return None, message
                else:
                    self.logger.info("Получены настройки от сервера.")
                    settings_json = response.json()

                    prepared_backup_folders = [
                        UnitForScanDTO(
                            folder_path=Path(item['folder_path']),
                            reqexp_pattern=item['reqexp_pattern'],
                            allowed_file_formats=tuple(
                                [
                                    file_format.strip()
                                    for file_format in item['allowed_file_formats'].split(',')
                                ]
                            )
                        )
                        for item in settings_json['backups']
                    ]

                    prepared_backup_tsm_log_files = [
                        UnitForTSMScanDTO(
                            log_file_name=str(item['log_file_name']),
                            path_to_log_file=Path(item['path_to_log_file']),
                        )
                        for item in settings_json['backup_tsm_log_files']
                    ]

                    all_settings = SettingsDTO(
                        api_endpoint_url=DBConnector.read_api_endpoint(),
                        # Логин для авторизации на стороне сервера
                        api_login=DBConnector.get_username(),
                        # Пароль для авторизации на стороне сервера
                        api_password=DBConnector.get_password(),
                        # Периодичность отправки статистики о бэкапах (в минутах)
                        backup_sending_minutes_frequency=settings_json['settings']['backup_sending_minutes_frequency'],
                        # Периодичность отправки статистики о железе и программах (в минутах)
                        stat_sending_minutes_frequency=settings_json['settings']['stat_sending_minutes_frequency'],
                        # Периодичность отправки сигнала присутствия (в минутах)
                        precision_sending_minutes_frequency=settings_json['settings'][
                            'precision_sending_minutes_frequency'],
                        # Периодичность отправки запроса настроек (в минутах)
                        ask_settings_minutes_frequency=settings_json['settings']['ask_settings_minutes_frequency'],
                        # Папки для сканирования бэкапов в них
                        backup_folders=prepared_backup_folders,
                        # Фалы логов TSM для сканирования бэкапов в них
                        backup_tsm_log_files=prepared_backup_tsm_log_files
                    )
                    return all_settings, None
        except requests.exceptions.ConnectionError:
            return None, None

    @staticmethod
    def launch(logger: Logger):
        return GetSettingsFromServer(logger=logger)._launch()


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
