from logging import Logger

from services_common.db_connector import DBConnector
from services_common.dto import SettingsDTO
from services_common.get_settings_from_server import GetSettingsFromServer
from services_common.read_settings import ReadSettingsFromBD
from services_common.write_settings_to_db import WriteSettingsToBD


class GetSettingsAndCheckItForChanges:
    """ Получит настройки с сервера и в случае если они поменялись поставит метку в БД для перезапуска работ. """

    def __init__(self, logger: Logger):
        self.logger = logger

    def run(self):
        request_result = GetSettingsFromServer.launch(logger=self.logger)
        if request_result[0] is None:
            self.logger.error(f"Ошибка получения настроек асистента с сервера: {request_result[1]}")
        else:
            server_settings = request_result[0]
            local_settings = ReadSettingsFromBD.run(logger=self.logger)
            # print(f"{server_settings=}")
            # print(f"l{local_settings=}")

            # Если настройки не идентичны, то презапишем их
            if not self.is_identical_settings(first_settings=server_settings, second_settings=local_settings):
                WriteSettingsToBD.after_changes_settings(
                    settings=server_settings
                )
                DBConnector.label_the_new_settings(label=True)
                message = (
                    f"Настройки на сервере поменялись.\n"
                    f"Было: "
                    f"\n\tbackup_sending_minutes_frequency: {local_settings.backup_sending_minutes_frequency}"
                    f"\n\tstat_sending_minutes_frequency: {local_settings.stat_sending_minutes_frequency}"
                    f"\n\tprecision_sending_minutes_frequency: {local_settings.precision_sending_minutes_frequency}"
                    f"\n\task_settings_minutes_frequency: {local_settings.ask_settings_minutes_frequency}"
                    f"\n\tbackup_folders: {local_settings.backup_folders}"
                    f"Записали: "
                    f"\n\tbackup_sending_minutes_frequency: {server_settings.backup_sending_minutes_frequency}"
                    f"\n\tstat_sending_minutes_frequency: {server_settings.stat_sending_minutes_frequency}"
                    f"\n\tprecision_sending_minutes_frequency: {server_settings.precision_sending_minutes_frequency}"
                    f"\n\task_settings_minutes_frequency: {server_settings.ask_settings_minutes_frequency}"
                    f"\n\tbackup_folders: {server_settings.backup_folders}"
                    f"\n\tlocal_settings: {local_settings}"
                    f"\n\tserver_settings: {server_settings}"
                )
                self.logger.info(message)
                print(message)
            else:
                message = f"Настройки на сервере не поменялись. "
                self.logger.info(message)
                # print(message)

    def is_identical_settings(self, first_settings: SettingsDTO, second_settings: SettingsDTO):
        """ Проверит, что данные в двух DTO идентичны. """
        return first_settings == second_settings


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
