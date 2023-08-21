import sys
import traceback
from json import JSONDecodeError
from logging import Logger


class ProgramLog:
    """ Класс для логирования ошиок вместе с traceback. """

    def __init__(self, logger: Logger, current_message: str = '', verbose: bool = True):
        self.logger = logger
        self.verbose = verbose
        self.error_type, self.error_value, self.error_trace = sys.exc_info()
        self.current_message = f"{current_message} "

    def _get_custom_traceback(self) -> str:
        self.logger.info(type(traceback.extract_tb(self.error_trace)), traceback.extract_tb(self.error_trace))
        custom_traceback = "\n"
        for line in [
            (item.filename, item.lineno, item.name, item._line)
            for item in traceback.extract_tb(self.error_trace)
        ]:
            custom_traceback = f"{custom_traceback}File {line[0]}, line {line[1]} in {line[2]}\n\t{line[3]}\n"

        return custom_traceback

    def info_program_log(self):
        self.logger.info(self.current_message)
        if self.verbose:
            print(self.current_message)

    def error_program_log(self):
        """ Запишет в логи ошибку асистента. """

        self.current_message = (f"{self.current_message} Type: {self.error_type} "
                                f"Value: {self.error_value}")
        if self.verbose:
            self.current_message = f"{self.current_message}\nTraceback: {self._get_custom_traceback()}"
            # print(self.current_message)

        self.logger.error(self.current_message)
        traceback.print_exception(self.error_type, self.error_value, self.error_trace, limit=5, file=sys.stdout)

    def critical_program_log(self):
        """ Запишет в логи ошибку асистента. """
        self.current_message = (f"{self.current_message} Type: {self.error_type} "
                                f"Value: {self.error_value}")
        if self.verbose:
            self.current_message = f"{self.current_message}\nTraceback: {self._get_custom_traceback()}"
            # print(self.current_message)

        self.logger.critical(self.current_message)
        traceback.print_exception(self.error_type, self.error_value, self.error_trace, limit=5, file=sys.stdout)

    def critical_response_log(self, response, endpoint_url: str, headers: dict, data: dict):
        """ Логирование ответа от requests """
        try:
            self.logger.critical(
                f"HTTP запрос на url {endpoint_url} вернул статус {response.status_code}. "
                f"\nОтвет сервера: {response.json()} "
                f"\nЗаголовки: {headers}"
                f"\nДанные: {data} "
            )
        except JSONDecodeError:
            self.logger.critical(
                f"HTTP запрос на url {endpoint_url} вернул статус {response.status_code}. "
                f"\nЗаголовки: {headers}"
                f"\nДанные: {data} "
            )
        except Exception:
            self.logger.critical(
                f"Не отловленая ошибка при запросе {response} с url {endpoint_url}"
            )


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
