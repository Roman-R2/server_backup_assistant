from logging import Logger
from urllib.parse import urlparse

from services_common.db_connector import DBConnector
from services_common.program_log import ProgramLog


class ServerEndpoint:
    """ Класс для преобразований api endpoints. """

    def __init__(self, logger: Logger):
        self.logger = logger

    def get_true_endpoint(self, add_string: str) -> str:
        """
        Вернет эндпоинт к серверу с добавленной строкой
        :param add_string: Строка, которую нужно добавить в эндпоинт
        :return: Целевой эндпоинт
        """
        server_api_endpoint = DBConnector.read_api_endpoint()

        if server_api_endpoint is None:
            message = f"api_endpoint прочитан из БД как None"
            ProgramLog(logger=self.logger, current_message=message).critical_program_log()
            raise ValueError(message)
        else:
            server_api_endpoint = urlparse(server_api_endpoint)

        return f'{server_api_endpoint.scheme}://{server_api_endpoint.netloc}/api/v1/{add_string}/'
