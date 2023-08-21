import json
from typing import Union, Tuple, Any
from urllib.parse import urlparse

import requests

from services_common.common_services import JsonHeaderMixin
from services_common.db_connector import DBConnector
from services_common.http_statuses import Status
from services_common.program_log import ProgramLog
from services_gui.gui_logger import GuiLogger

LOGGER = GuiLogger().get_logger()


class TokenSaveMethod:
    """ Метод обработки и сохранения полученного токена. """
    BD = 'bd'
    FILE = 'file'


class ServerAuthorizationV2(JsonHeaderMixin):
    """ Занимается фаторизацией ассистента на сервере для передачи данных. Вторая версия класса. """

    def __init__(self, api_endpoint, username, password, method=TokenSaveMethod.BD):
        super().__init__()
        self.api_endpoint = urlparse(api_endpoint)
        self.username = username
        self.password = password
        self.method = method
        self.api_auth_token_url = rf'{self.api_endpoint.scheme}://{self.api_endpoint.netloc}/api-auth-token/'

        self.user_auth_data = {
            "username": self.username,
            "password": self.password
        }

    def get_token(self) -> str:
        """ Получит токен для авторизации """
        if self.method is TokenSaveMethod.BD:
            return self.__get_token_from_db()
        if self.method is TokenSaveMethod.FILE:
            return ""

    @staticmethod
    def renew_token(api_endpoint, username, password, method=TokenSaveMethod.BD) -> Union[
        Tuple[None, str], Tuple[Any, None]]:
        return ServerAuthorizationV2(api_endpoint, username, password, method)._renew_token()

    def _renew_token(self):
        """
        Обновит токен для указанного в настройках пользователя.
        :return: str
        """
        try:
            with requests.post(
                    self.api_auth_token_url,
                    data=json.dumps(self.user_auth_data, indent=4, sort_keys=True, default=str),
                    headers=self.headers
            ) as response:
                if response.status_code != Status.HTTP_200_OK:
                    ProgramLog(logger=LOGGER).critical_response_log(
                        response=response,
                        endpoint_url=self.api_auth_token_url,
                        headers=self.headers,
                        data=self.user_auth_data,
                    )
                    message = (
                        f"При обновлении токена по пути "
                        f"{self.api_auth_token_url} "
                        f"получен HTTP статус {response.status_code}\n"
                        f"(ожидался 200 OK)\n"
                        f"{response.json()}")
                    return None, message
                else:
                    token = response.json()['token']
                    if self.method is TokenSaveMethod.BD:
                        self.__save_token_to_db(token)
                        return token, None
                    # if self.method is TokenSaveMethod.FILE:
                    #     self.__save_token_to_file(token)
                    #     return token, None
                    LOGGER.info("Токен авторизации обновлен.")
        except (requests.exceptions.ConnectionError, AttributeError):
            error_message = "Ошибка обновления токена на сервере, проверьте соединение."
            ProgramLog(
                current_message=f"{error_message} "
                              f"Url: {self.api_auth_token_url} "
                              f"Headers: {self.headers} "
                              f"Data: {self.user_auth_data}",
                verbose=False,
                logger=LOGGER
            ).critical_program_log()
            # Ждем час и снова пытаемся обновить токен
            # sleep(3600)
            # self.renew_token()
            return None, error_message

    def __save_token_to_db(self, token: str) -> None:
        """ Сохранит токен в базу данных. """
        DBConnector().save_token(token)

    # def __save_token_to_file(self, token: str) -> None:
    #     """ Сохранит токен в определенный файл. """
    #     with Settings.TOKEN_FILE.open(mode='w', encoding=Settings.COMMON_ENCODING) as fd:
    #         fd.write(token)

    def __get_token_from_db(self) -> str:
        """ Прочитает токен из базы данных. """
        token = DBConnector().get_token()
        return token


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
