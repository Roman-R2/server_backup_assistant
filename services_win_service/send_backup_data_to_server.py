import json
import os
from datetime import datetime
from typing import List

import requests

from services_common.common_services import JsonHeaderMixin, AddTokenToHeaderMixin
from services_common.dto import SettingsDTO, UnitForScanDTO, FileStatDTO
from services_common.http_statuses import Status
from services_common.program_log import ProgramLog
from services_win_service.service_logger import ServiceLogger

LOGGER = ServiceLogger().get_logger()


class SendBackupDataToServer(JsonHeaderMixin, AddTokenToHeaderMixin):
    """ Осуществляет отправку данных о состоянии бэкапов на сервер. """

    def __init__(self, settings: SettingsDTO, server_data: UnitForScanDTO, prepared_files: List[FileStatDTO]):
        super().__init__()
        self.settings = settings
        self.server_url: str = os.path.join(settings.api_endpoint_url, 'backups/')
        self.server_data: UnitForScanDTO = server_data

        data = {
            "token": self.token,
            "data_formed_at": datetime.now(),
            "backup_folder": server_data.folder_path,
            "backup_files": prepared_files
        }

        try:
            with requests.post(
                    url=self.server_url,
                    data=json.dumps(data, indent=4, sort_keys=True, default=str),
                    headers=self.headers,
            ) as response:

                if response.status_code != Status.HTTP_201_CREATED:
                    ProgramLog(logger=LOGGER).critical_response_log(
                        response=response,
                        endpoint_url=self.server_url,
                        headers=self.headers,
                        data=data
                    )
                else:
                    success_message = (
                        f"Отправлены данные бэкапов на {self.server_url} (HTTP статус ответа {response.status_code})"
                    )
                    LOGGER.info(success_message)
                    print(success_message)
        except (requests.exceptions.ConnectionError, AttributeError):
            error_message = f"Периодические данные о состоянии бэкапов не отправлены"
            ProgramLog(logger=LOGGER, current_message=error_message, verbose=False).error_program_log()


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
