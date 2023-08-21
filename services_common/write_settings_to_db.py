from urllib.parse import urlparse

from services_common.db_connector import DBConnector
from services_common.dto import SettingsDTO


class WriteSettingsToBD:
    """ Запишет настройки асистента в локальную БД. """

    def __init__(
            self,
            api_endpoint="",
            api_login="",
            api_password="",
            backup_sending_minutes_frequency=2,
            stat_sending_minutes_frequency=1,
            precision_sending_minutes_frequency=1,
            ask_settings_minutes_frequency=10,
            backup_folders=None,
            backup_tsm_log_files=None

    ):
        self.backup_sending_minutes_frequency = backup_sending_minutes_frequency
        self.stat_sending_minutes_frequency = stat_sending_minutes_frequency
        self.precision_sending_minutes_frequency = precision_sending_minutes_frequency
        self.ask_settings_minutes_frequency = ask_settings_minutes_frequency
        self.backup_folders = [] if backup_folders is None else backup_folders
        self.backup_tsm_log_files = [] if backup_tsm_log_files is None else backup_tsm_log_files

        self.api_endpoint = urlparse(api_endpoint)
        self.api_login = api_login
        self.api_password = api_password

    def _after_authorization(self):
        """ Запишем некоторые настройки (api endpoint, username, password) в БД после ваторизации. """
        DBConnector().write_data_after_authorization(
            api_endpoint=f'{self.api_endpoint.scheme}://{self.api_endpoint.netloc}/api/v1/',
            api_login=self.api_login,
            api_password=self.api_password
        )

    @staticmethod
    def after_authorization(api_endpoint, api_login, api_password):
        return WriteSettingsToBD(
            api_endpoint=api_endpoint,
            api_login=api_login,
            api_password=api_password
        )._after_authorization()

    def _after_read_settings(self):
        DBConnector().write_data_after_read_settings(
            backup_sending_minutes_frequency=self.backup_sending_minutes_frequency,
            stat_sending_minutes_frequency=self.stat_sending_minutes_frequency,
            precision_sending_minutes_frequency=self.precision_sending_minutes_frequency,
            ask_settings_minutes_frequency=self.ask_settings_minutes_frequency,
            backup_folders=self.backup_folders,
            backup_tsm_log_files=self.backup_tsm_log_files
        )

    @staticmethod
    def after_read_settings(settings: SettingsDTO):
        return WriteSettingsToBD(
            backup_sending_minutes_frequency=settings.backup_sending_minutes_frequency,
            stat_sending_minutes_frequency=settings.stat_sending_minutes_frequency,
            precision_sending_minutes_frequency=settings.precision_sending_minutes_frequency,
            ask_settings_minutes_frequency=settings.ask_settings_minutes_frequency,
            backup_folders=settings.backup_folders,
            backup_tsm_log_files=settings.backup_tsm_log_files
        )._after_read_settings()

    def _after_changes_settings(self):
        DBConnector().write_data_after_read_settings(
            backup_sending_minutes_frequency=self.backup_sending_minutes_frequency,
            stat_sending_minutes_frequency=self.stat_sending_minutes_frequency,
            precision_sending_minutes_frequency=self.precision_sending_minutes_frequency,
            ask_settings_minutes_frequency=self.ask_settings_minutes_frequency,
            backup_folders=self.backup_folders,
            backup_tsm_log_files=self.backup_tsm_log_files
        )

    @staticmethod
    def after_changes_settings(settings: SettingsDTO):
        return WriteSettingsToBD(
            backup_sending_minutes_frequency=settings.backup_sending_minutes_frequency,
            stat_sending_minutes_frequency=settings.stat_sending_minutes_frequency,
            precision_sending_minutes_frequency=settings.precision_sending_minutes_frequency,
            ask_settings_minutes_frequency=settings.ask_settings_minutes_frequency,
            backup_folders=settings.backup_folders,
            backup_tsm_log_files=settings.backup_tsm_log_files
        )._after_read_settings()


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
