import json
import os
from datetime import datetime

import requests

from services_common.common_services import JsonHeaderMixin, AddTokenToHeaderMixin
from services_common.dto import SettingsDTO, UnitForTSMScanDTO
from services_common.http_statuses import Status
from services_common.program_log import ProgramLog
from services_win_service.service_logger import ServiceLogger

LOGGER = ServiceLogger().get_logger()


class SendBackupTSMLogDataToServer(JsonHeaderMixin, AddTokenToHeaderMixin):
    """ Осуществляет отправку данных о состоянии бэкапов на сервер. """

    def __init__(self, settings: SettingsDTO, server_data: UnitForTSMScanDTO, last_backup_log: list):
        super().__init__()
        self.settings = settings
        self.server_url: str = os.path.join(settings.api_endpoint_url, 'backups_tsm_logs/')
        self.server_data: UnitForTSMScanDTO = server_data
        self.last_backup_log = last_backup_log

        data = {
            "token": self.token,
            "data_formed_at": datetime.now(),
            "path_to_log_file": server_data.path_to_log_file,
            "last_backup_log": last_backup_log
        }

        # print(f"{data=}")
        # print(f"{json.dumps(data, default=str)=}")

        # print(f"{prepared_files=}")

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
                        f"Отправлены данные бэкапов TSM файлов логов на "
                        f"{self.server_url} (HTTP статус ответа {response.status_code})"
                    )
                    LOGGER.info(success_message)
                    print(success_message)
        except (requests.exceptions.ConnectionError, AttributeError):
            error_message = f"Периодические данные о состоянии бэкапов TSM файлов логов не отправлены"
            ProgramLog(logger=LOGGER, current_message=error_message, verbose=False).error_program_log()


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
