from logging import Logger
from pathlib import Path

from services_common.db_connector import DBConnector
from services_common.dto import SettingsDTO, UnitForScanDTO, UnitForTSMScanDTO


class ReadSettingsFromBD:
    """ Прочтет настройки для асистента из локальной БД. """

    def __init__(self, logger: Logger):
        self.logger = logger

    @staticmethod
    def run(logger: Logger):
        return ReadSettingsFromBD(logger=logger)._run()

    def _run(self) -> SettingsDTO:
        backup_settings_db_obj = DBConnector().read_backup_settings()

        backup_tsl_log_settings_db_obj = DBConnector().read_backup_tsm_log_settings()

        if backup_settings_db_obj:
            backup_folders_setting_list = [
                UnitForScanDTO(
                    folder_path=Path(item.folder_path),
                    reqexp_pattern=item.reqexp_pattern.strip(),
                    allowed_file_formats=tuple([item.strip() for item in str(item.allowed_file_formats).split(',')])
                )
                for item in backup_settings_db_obj
            ]
        else:
            backup_folders_setting_list = []

        backup_tsm_log_settings_db_obj = DBConnector().read_backup_tsm_log_settings()

        if backup_tsm_log_settings_db_obj:
            backup_tsl_logs_setting_list = [
                UnitForTSMScanDTO(
                    log_file_name=str(item.log_file_name),
                    path_to_log_file=Path(item.path_to_log_file)
                )
                for item in backup_tsl_log_settings_db_obj
            ]
        else:
            backup_tsl_logs_setting_list = []

        all_settings_bd_obj = DBConnector().read_common_settings()

        if all_settings_bd_obj:
            all_settings = SettingsDTO(
                api_endpoint_url=all_settings_bd_obj.api_endpoint,
                # Логин для авторизации на стороне сервера
                api_login=all_settings_bd_obj.api_login,
                # Пароль для авторизации на стороне сервера
                api_password=all_settings_bd_obj.api_password,
                # Периодичность отправки статистики о бэкапах (в минутах)
                backup_sending_minutes_frequency=all_settings_bd_obj.backup_sending_minutes_frequency,
                # Периодичность отправки статистики о железе и программах (в минутах)
                stat_sending_minutes_frequency=all_settings_bd_obj.stat_sending_minutes_frequency,
                # Периодичность отправки сигнала присутствия (в минутах)
                precision_sending_minutes_frequency=all_settings_bd_obj.precision_sending_minutes_frequency,
                # Периодичность отправки запроса настроек (в минутах)
                ask_settings_minutes_frequency=all_settings_bd_obj.ask_settings_minutes_frequency,
                # Папки для сканирования бэкапов в них
                backup_folders=backup_folders_setting_list,
                # Фалы логов TSM для сканирования бэкапов в них
                backup_tsm_log_files=backup_tsl_logs_setting_list,
            )
        else:
            self.logger.critical("Нет настроек асистента в базе данных.")
            exit(25)

        return all_settings


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
