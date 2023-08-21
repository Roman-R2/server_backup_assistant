import os
import sys
import time

import requests
from dotenv import load_dotenv

import win32serviceutil  # ServiceFramework and commandline helper
import win32service  # Events
import servicemanager  # Simple setup and logging

from services_common.common_settings import Settings
from services_common.dto import SettingsDTO
from services_common.get_settings_from_server import GetSettingsFromServer
from services_common.inprove_tz_for_py_installer import TZImproveForPyInstaller
from services_common.program_log import ProgramLog
from services_win_service.server_assistant_worker import ServerAssistantWorker
from services_win_service.service_logger import ServiceLogger

load_dotenv(Settings.BASE_DIR / '.env')

LOGGER = ServiceLogger().get_logger()


class MyService:
    """ Service description. """

    def stop(self):
        """Stop the service"""
        self.running = False

    def run(self):
        """Main service loop."""
        self.running = True
        while self.running:
            try:
                # print("I'am here")
                # time.sleep(1)
                message = f"Пытаемся получить настройки приложения в службе windows..."
                LOGGER.info(message)

                # Получить настройки асистента с сервера
                settings = GetSettingsFromServer.launch(logger=LOGGER)
                if settings[0] is None:
                    LOGGER.info(f"Ошибка настроек: {settings[1]}")
                else:
                    received_settings: SettingsDTO = settings[0]

                    message = f"Выполняем работы службы..."
                    servicemanager.LogInfoMsg("message")
                    LOGGER.info(message)

                    # Запустить процесс сбора данных
                    # th1 = threading.Thread(
                    #     target=ServerAssistantWorker.launch,
                    #     kwargs={'settings': received_settings},
                    #     daemon=True
                    # )
                    # th1.start()
                    ServerAssistantWorker.launch(settings=received_settings)
            except requests.exceptions.ConnectionError:
                minute1 = 60
                # minutes10 = 10 * minute1
                ProgramLog(
                    logger=LOGGER,
                    current_message=(
                        f'ConnectionError. '
                        f'Возможно сервер ПК Наблюдатель отключен или не отвечает. '
                        f'Ждем {minute1} секунд и пробуем снова.'
                    )
                ).error_program_log()
                # Ждем
                time.sleep(minute1)


class MyServiceFramework(win32serviceutil.ServiceFramework):
    _svc_name_ = f"{os.getenv('PRODUCT_NAME_SERVICE', default='R2ZiD_service')}"
    _svc_display_name_ = f"{os.getenv('PRODUCT_NAME_SERVICE', default='R2ZiD_service')}"

    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.service_impl.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        LOGGER.info(f"Служба {os.getenv('PRODUCT_NAME_SERVICE', default='R2ZiD_service')} остановлена")

    def SvcDoRun(self):
        """Start the service; does not return until stopped"""
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.service_impl = MyService()
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        # Run the service
        self.service_impl.run()
        LOGGER.info(f"Служба {os.getenv('PRODUCT_NAME_SERVICE', default='R2ZiD_service')} запущена")


def init():
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MyServiceFramework)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MyServiceFramework)


if __name__ == '__main__':
    try:
        # исправим временное смещение, если оно ноль на то что в переменных окружения часов
        # (на некоторых серверах не подтягиваются в приложения смещения временной зоны)
        TZImproveForPyInstaller(logger=LOGGER, verbose=True).improve()
        LOGGER.info(" Запускаем службу асистента ПК Наблюдатель ".center(100, '-'))
        init()
        # MyService().run()
    except Exception:
        ProgramLog(logger=LOGGER, current_message=f'Неизвестная ошибка Exception...').error_program_log()
