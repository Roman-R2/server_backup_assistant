import json
import os

import requests

from services_common.common_services import JsonHeaderMixin, AddTokenToHeaderMixin
from services_common.dto import SettingsDTO
from services_common.http_statuses import Status
from services_common.program_log import ProgramLog
from services_win_service.server_stat_assistant import ServerWinStatAssistant
from services_win_service.service_logger import ServiceLogger

LOGGER = ServiceLogger().get_logger()


class SendStatDataToServer(JsonHeaderMixin, AddTokenToHeaderMixin):
    """ Осуществляет отправку данных о состоянии железа и программ сервера. """

    def __init__(self, settings: SettingsDTO):
        super().__init__()
        self.settings = settings
        self.server_url: str = os.path.join(settings.api_endpoint_url, 'stats/')
        data = ServerWinStatAssistant(
            assistant_auth_token=self.token
        ).get_statistics()._asdict()

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
                        f"Отправлена статистика сервера на {self.server_url} (HTTP статус ответа {response.status_code})"
                    )
                    LOGGER.info(success_message)
                    print(success_message)
        except (requests.exceptions.ConnectionError, AttributeError):
            error_message = f"Перилдические данные о состоянии железа и программ"
            ProgramLog(logger=LOGGER, current_message=error_message, verbose=False).error_program_log()


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
