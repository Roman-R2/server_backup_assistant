import json
import os
import socket

import requests

from services_common.db_connector import DBConnector
from services_common.dto import SettingsDTO
from services_common.http_statuses import Status
from services_common.program_log import ProgramLog
from services_win_service.service_logger import ServiceLogger

LOGGER = ServiceLogger().get_logger()


class SendPresenceToServer:
    """ Осуществляет отправку данных о присутствии асистента. """
    headers = {'Content-type': 'application/json'}

    def __init__(self, settings: SettingsDTO):
        self.settings = settings
        self.server_url: str = os.path.join(settings.api_endpoint_url, 'iamhere/')
        token = DBConnector.get_token()
        ip_address = socket.gethostbyname(socket.gethostname())
        data = {
            "token": token,
            "assistant_ip": ip_address
        }

        self.headers['Authorization'] = f'Token {token}'

        try:
            with requests.put(
                    self.server_url,
                    data=json.dumps(data, indent=4, sort_keys=True, default=str),
                    headers=self.headers) as response:

                if response.status_code != Status.HTTP_200_OK:
                    ProgramLog(logger=LOGGER).critical_response_log(
                        response=response,
                        endpoint_url=self.server_url,
                        headers=self.headers,
                        data=data
                    )
                else:
                    message = f"Отправлены данные присутствия асистента на сервер {self.server_url}."
                    LOGGER.info(message)
                    print(message)

        except (requests.exceptions.ConnectionError, AttributeError):
            error_message = f"Перилдические данные о присутствии не отправлены"
            ProgramLog(logger=LOGGER, current_message=error_message, verbose=False).error_program_log()


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
