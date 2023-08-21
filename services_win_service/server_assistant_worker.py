import os
import time
from datetime import datetime

import schedule

from services_common.common_settings import Settings
from services_common.db_connector import DBConnector
from services_common.dto import SettingsDTO
from services_common.get_settings_and_check_it_for_changes import GetSettingsAndCheckItForChanges
from services_common.get_settings_from_server import GetSettingsFromServer
from services_common.inprove_tz_for_py_installer import TZImproveForPyInstaller
from services_common.read_settings import ReadSettingsFromBD
from services_win_service.folder_scanner import FolderScanner
from services_win_service.send_precision_to_server import SendPresenceToServer
from services_win_service.send_stat_data_to_server import SendStatDataToServer
from services_win_service.service_logger import ServiceLogger


os.environ['TZ'] = Settings.OS_ENVIRON_TZ

LOGGER = ServiceLogger().get_logger()


class ServerAssistantWorker:
    """ Предназначен для сканирования папок из преданного списка на предмет новых данных в этих папках."""

    def __init__(self, settings: SettingsDTO) -> None:
        self.settings: SettingsDTO = settings

    def backup_scanner_job(self):
        """ Работа по сканированию папок быкапов и отправке данных. """
        LOGGER.info(f'Выполняем работу по сбору данных бэкапов, указанных в настройках. '
                    f'(Папки бэкапов {len(self.settings.backup_folders)} шт. '
                    f'Лог файлы от TSM {len(self.settings.backup_tsm_log_files)} шт.)')
        # Начнем работу по сканированию папок бэкапов
        FolderScanner(settings=self.settings).scan_folders_job()

    def server_stat_scanner_job(self):
        """ Работа по сканированию статистики о серверном железе и программах и отправке данных. """
        LOGGER.info('Начинаем собитать статистику о серверном железе и программах.')
        # Отправим данные о железе сервера
        SendStatDataToServer(
            settings=self.settings,
        )

    def iamhere_presence_job(self):
        """ Рибота по отправки сообщения о присутствии асистента. """
        SendPresenceToServer(settings=self.settings)

    def ask_for_renew_assistant_setting_job(self):
        """ Рибота по получению настроек с сервера-наблюдателя,
        их сравнения с текущими и в случае их обновления - перезаписив  базу и перезапуску работ. """
        GetSettingsAndCheckItForChanges(logger=LOGGER).run()

    def run_jobs_exclude_settings_check(self):
        """ Вернет список всех работ, кроме проверки настроек асистента """
        job_list = [
            schedule.every(
                self.settings.backup_sending_minutes_frequency
            ).minutes.do(self.backup_scanner_job),
            schedule.every(
                self.settings.stat_sending_minutes_frequency
            ).minutes.do(self.server_stat_scanner_job),
            schedule.every(
                self.settings.precision_sending_minutes_frequency
            ).minutes.do(self.iamhere_presence_job)
        ]
        return job_list

    def stop_jobs(self, job_list: list):
        """ Отменит работы из переданного списка  """
        for item in job_list:
            schedule.cancel_job(item)

    @staticmethod
    def launch(settings: SettingsDTO) -> None:
        return ServerAssistantWorker(settings)._launch()

    def _launch(self) -> None:
        TZImproveForPyInstaller(verbose=True, logger=LOGGER).improve()

        start_message = (
            f"\n{' Assistant worker started '.center(79, '-')}"
            f"\nНачинаем с настройками для {self.settings.api_login}: "
            f"\n\tЧастота проверки бэкапов и отправки статистики: раз в {self.settings.backup_sending_minutes_frequency} минут"
            f"\n\tЧастота отправки статистики по оборудованию: раз в {self.settings.stat_sending_minutes_frequency} минут"
            f"\n\tЧастота опроса сервера о новых настройках для асистента: раз в {self.settings.ask_settings_minutes_frequency} минут"
            f"\n\tОтслеживаемые папки с бэкапами: {self.settings.backup_folders}"
            f"\n\tОтслеживаемые файлы логов TSM: {self.settings.backup_tsm_log_files}"
            f"\n{'-'.center(79, '-')}"
        )
        print(start_message)
        LOGGER.info(start_message)

        schedule.every(
            self.settings.ask_settings_minutes_frequency
        ).minutes.do(self.ask_for_renew_assistant_setting_job)
        jobs_list_exclude_settings_check = self.run_jobs_exclude_settings_check()

        # Запустим один раз все работы при старте асистента
        self.iamhere_presence_job()
        self.backup_scanner_job()
        self.server_stat_scanner_job()

        while True:
            schedule.run_pending()

            print(f"\n{datetime.now()}")
            for num, item in enumerate(schedule.jobs, start=1):
                print(
                    f"\t{num}. "
                    f"{item.job_func.__name__}: {item.interval} "
                    f"{item.unit}  "
                    f"last run: {item.latest} "
                    f"next run: {item.next_run}"
                )

            time.sleep(10)
            if DBConnector.get_settings_label():
                # print('-----> REFRESH JOBS', datetime.now(), schedule.jobs)

                # Если настройки обновились, то прочтем их заново и запустим работы с новыми настройками
                self.stop_jobs(jobs_list_exclude_settings_check)
                self.settings = ReadSettingsFromBD.run(logger=LOGGER)
                jobs_list_exclude_settings_check = self.run_jobs_exclude_settings_check()
                DBConnector.label_the_new_settings(label=False)


if __name__ == '__main__':
    # print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
    ServerAssistantWorker.launch(settings=GetSettingsFromServer.launch(logger=LOGGER)[0])
