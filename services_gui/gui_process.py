import os

import psutil

from services_common.program_log import ProgramLog
from services_gui.gui_logger import GuiLogger

LOGGER = GuiLogger().get_logger()


class GuiProcess:
    """ Класс объединяет логику по работе с процессом приложения GUI. """

    def get_current_process_name(self):
        """ Вернет имя текущего процесса. """
        if os.getenv('ASSISTANT_NAME_GUI') is not None:
            assistant_name_gui = os.getenv('ASSISTANT_NAME_GUI')
            return f"{assistant_name_gui}.exe"
        # elif os.getenv('ASSISTANT_VERSION') is not None:
        #     assistant_version = os.getenv('ASSISTANT_VERSION')
        else:
            message = f"Не получены переменные окружения для имени процесса"
            ProgramLog(logger=LOGGER, current_message=message)
            raise ValueError()

    def is_app_process_already_exists(self):
        """ Проверит, запущен ли уже процесс данного приложения. """

        current_process_obj = psutil.Process()

        similar_pid_list = [p.pid for p in psutil.process_iter() if p.name() == self.get_current_process_name()]

        if current_process_obj.pid in similar_pid_list:
            similar_pid_list.remove(current_process_obj.pid)

        resolution = True if similar_pid_list else False

        if resolution:
            LOGGER.info(
                f"Попытка запуска нового экземпляра процесса асистента при том, что он уже запущен. "
                f"Запуск остановлен.\n"
                f"Подобные pid: {similar_pid_list}\n "
                f"Объект текущего процесса: {current_process_obj}"
            )

        return resolution


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
