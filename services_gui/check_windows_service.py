import time

import psutil
import schedule

import customtkinter
from services_common.program_log import ProgramLog
from services_gui.gui_logger import GuiLogger

LOGGER = GuiLogger().get_logger()


class CheckWindowsService:
    """ Проверяет работы службы, которыя отвечает за отправку статистики. """

    def __init__(self, service_name: str, app_gui_window_obj: customtkinter.CTk):
        self.service_name = service_name
        self.app_gui_window_obj = app_gui_window_obj

    def get_service(self):
        service = None
        try:
            service = psutil.win_service_get(self.service_name)
            service = service.as_dict()
        except Exception as ex:
            # ProgramLog(logger=LOGGER, current_message=str(ex)).info_program_log()
            pass

        return service

    def __is_running(self):
        return True if self.get_service() and self.get_service()['status'] == 'running' else False

    def __is_exists(self):
        return True if self.get_service() else False

    @staticmethod
    def is_running(service_name: str, app_gui_window_obj: customtkinter.CTk):
        return CheckWindowsService(service_name=service_name, app_gui_window_obj=app_gui_window_obj).__is_running()

    @staticmethod
    def is_exists(service_name: str, app_gui_window_obj: customtkinter.CTk):
        return CheckWindowsService(service_name=service_name, app_gui_window_obj=app_gui_window_obj).__is_exists()

    def watch_for_windows_service(self):
        if self.__is_running():
            self.app_gui_window_obj.win_service_status.configure(text='  Запушен')
            self.app_gui_window_obj.win_service_status.configure(
                image=self.app_gui_window_obj.started_win_service_image
            )
        else:
            self.app_gui_window_obj.win_service_status.configure(text='  Остановлен')
            self.app_gui_window_obj.win_service_status.configure(
                image=self.app_gui_window_obj.stopped_win_service_image
            )

    def __run(self):
        """ Запуск отслеживания службы. """

        schedule.every(1).seconds.do(self.watch_for_windows_service)

        while True:
            schedule.run_pending()
            time.sleep(1)

    @staticmethod
    def run(service_name: str, app_gui_window_obj: customtkinter.CTk):
        return CheckWindowsService(service_name=service_name, app_gui_window_obj=app_gui_window_obj).__run()


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
    # CheckWindowsService.run()
