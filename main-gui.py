import concurrent.futures
import os
import subprocess
import threading

import psutil
import pyuac
from dotenv import load_dotenv

from pathlib import Path

import customtkinter
from PIL import Image

import pystray

from services_common.common_settings import Settings
from services_common.db_connector import DBConnector
from services_common.get_settings_from_server import GetSettingsFromServer
from services_common.inprove_tz_for_py_installer import TZImproveForPyInstaller
from services_common.program_log import ProgramLog
from services_common.write_settings_to_db import WriteSettingsToBD
from services_gui.check_windows_service import CheckWindowsService
from services_gui.get_default_server_url import GetDefaultServerUrl
from services_gui.gui_logger import GuiLogger
from services_gui.gui_process import GuiProcess
from services_gui.server_authorization import TokenSaveMethod, ServerAuthorizationV2

LOGGER = GuiLogger().get_logger()

load_dotenv(Settings.BASE_DIR / '.env')


class AppGUI(customtkinter.CTk):
    width = 900
    height = 600

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon = None
        self.title("Асистент ПК Наблюдатель")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)

        current_path = Path(__file__).parent
        self.bg_image = customtkinter.CTkImage(
            Image.open(current_path / "assets/background/bg_gradient.jpg"),
            size=(self.width, self.height)
        )
        self.bg_image_label = customtkinter.CTkLabel(self, image=self.bg_image)
        self.bg_image_label.grid(row=0, column=0)

        # START ------------- create login frame
        self.login_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.login_frame.grid(row=0, column=0, sticky="ns")
        self.login_label = customtkinter.CTkLabel(
            self.login_frame, text="Асистент\nПК Наблюдатель",
            font=customtkinter.CTkFont(size=20, weight="bold")
        )
        self.login_label.grid(row=0, column=0, padx=30, pady=(70, 15))
        self.username_entry = customtkinter.CTkEntry(self.login_frame, width=300, placeholder_text="Имя")
        self.username_entry.grid(row=1, column=0, padx=30, pady=(15, 15))
        self.username_entry.bind(sequence="<Return>", command=self.login_event)
        self.username_entry.insert(0, DBConnector.get_username())
        self.password_entry = customtkinter.CTkEntry(self.login_frame, width=300, show="*", placeholder_text="Пароль")
        self.password_entry.grid(row=2, column=0, padx=30, pady=(0, 15))
        self.password_entry.insert(0, '')
        # self.password_entry.insert(0, DBConnector.get_password())
        self.password_entry.bind(sequence="<Return>", command=self.login_event)
        self.login_button = customtkinter.CTkButton(self.login_frame, text="Войти", command=self.login_event, width=200)
        self.login_button.grid(row=3, column=0, padx=30, pady=(15, 15))
        self.api_endpoint_label = customtkinter.CTkLabel(
            self.login_frame, text="URL к серверу ПК Наблюдатель:",
            font=customtkinter.CTkFont(size=14, weight="normal")
        )
        self.api_endpoint_label.grid(row=4, column=0, padx=30, pady=(70, 0))
        self.api_endpoint_entry = customtkinter.CTkEntry(
            self.login_frame,
            width=300,
            placeholder_text="URL сервера-наблюдателя"
        )
        self.api_endpoint_entry.grid(row=5, column=0, padx=30, pady=(0, 15))
        self.api_endpoint_entry.insert(0, GetDefaultServerUrl.from_file())
        self.error_textbox = customtkinter.CTkTextbox(
            self.login_frame,
            width=300,
            height=150,
            text_color='red'
        )
        self.error_textbox.grid(row=6, column=0, padx=30, pady=(5, 5))
        # END ------------- create login frame

        # START ------------- create main frame
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        # self.main_label = customtkinter.CTkLabel(
        #     self.main_frame, text="Параметры асистента\n",
        #     font=customtkinter.CTkFont(size=20, weight="bold")
        # )
        # self.main_label.grid(row=0, column=0, padx=30, pady=(30, 15))

        self.stopped_win_service_image = customtkinter.CTkImage(
            Image.open(Settings.GUI_IMAGE_FOLDER / 'stopped.png'),
            size=(26, 26)
        )
        self.started_win_service_image = customtkinter.CTkImage(
            Image.open(Settings.GUI_IMAGE_FOLDER / 'started.png'),
            size=(26, 26)
        )
        self.win_service_status = customtkinter.CTkLabel(
            self.main_frame,
            text="  Остановлен",
            image=self.stopped_win_service_image,
            compound="left",
            font=customtkinter.CTkFont(size=15, weight="bold")
        )
        self.win_service_status.grid(row=1, column=0, padx=30, pady=20)

        self.start_assistant_service_button = customtkinter.CTkButton(
            master=self.main_frame,
            text="start service",
            command=self.start_service
        )
        self.start_assistant_service_button.grid(row=2, column=0, padx=30, pady=(0, 15), sticky="w")

        self.stop_assistant_service_button = customtkinter.CTkButton(
            master=self.main_frame,
            text="stop service",
            command=self.stop_service
        )
        self.stop_assistant_service_button.grid(row=3, column=0, padx=30, pady=(0, 15), sticky="w")
        self.stop_assistant_service_button = customtkinter.CTkButton(
            master=self.main_frame,
            text="debug service",
            command=self.debug_service
        )
        self.stop_assistant_service_button.grid(row=4, column=0, padx=30, pady=(0, 15), sticky="w")

        # self.assistant_token_label = customtkinter.CTkLabel(
        #     self.main_frame,
        #     text="Токен авторизации асистента",
        #     font=customtkinter.CTkFont(size=14, weight="normal")
        # )
        # self.assistant_token_label.grid(row=1, column=0, padx=30, pady=(0, 0))
        #
        # self.assistant_token_field = customtkinter.CTkEntry(self.main_frame, width=400,
        #                                                     placeholder_text="Токен авторизации асистента")
        # self.assistant_token_field.grid(row=2, column=0, padx=30, pady=(0, 15))
        # self.assistant_token_field.insert(0, DBConnector.get_token())
        # self.renew_token_button = customtkinter.CTkButton(
        #     master=self.main_frame,
        #     text="показать токен",
        #     fg_color="transparent",
        #     border_width=2,
        #     text_color=("gray10", "#DCE4EE"),
        #     command=self.renew_token
        # )
        # self.renew_token_button.grid(row=2, column=1, padx=30, pady=(0, 15), sticky="s")

        # self.assistant_crypto_token_label = customtkinter.CTkLabel(
        #     self.main_frame,
        #     text="Токен для шифрования",
        #     font=customtkinter.CTkFont(size=14, weight="normal")
        # )
        # self.assistant_crypto_token_label.grid(row=3, column=0, padx=30, pady=(0, 0))
        #
        # self.assistant_crypto_token_field = customtkinter.CTkEntry(self.main_frame, width=400,
        #                                                            placeholder_text="Токен для шифрования")
        # self.assistant_crypto_token_field.grid(row=4, column=0, padx=30, pady=(0, 15))
        # self.assistant_crypto_token_field.insert(0, "none")

        # self.login_event()

        # self.back_button = customtkinter.CTkButton(self.main_frame, text="Back", command=self.back_event, width=300)
        # self.back_button.grid(row=2, column=0, padx=30, pady=(15, 15))
        # END ------------- create main frame

        self.image = Image.open(Settings.GUI_IMAGE_FOLDER / "app-icon.png")
        self.menu = (
            pystray.MenuItem('Показать', self.show_window),
            pystray.MenuItem('Закрыть', self.quit_window)
        )
        self.protocol('WM_DELETE_WINDOW', self.withdraw_window)
        self.mainloop()

    def start_service(self):
        if not pyuac.isUserAdmin():
            message = f"Запустите асистента с правами администратора..."
            ProgramLog(logger=LOGGER, current_message=message).error_program_log()
            raise PermissionError(message)

        command_to_execute = [
            "!install_and_run_service.bat",
        ]

        LOGGER.info(f"Выполняем команды {' '.join(command_to_execute)}")

        try:
            run: subprocess.CompletedProcess = subprocess.run(command_to_execute, capture_output=True)
            if run.returncode == 0:
                LOGGER.info(f"Команды {' '.join(command_to_execute)} выполнены успешно.")
            else:
                LOGGER.error(f"Проблема выполнения команд {' '.join(command_to_execute)}. returncode={run.returncode}")
        except Exception:
            message = "Exception start_service"
            ProgramLog(logger=LOGGER, current_message=message).error_program_log()
            raise Exception(message)

    def stop_service(self):
        if not pyuac.isUserAdmin():
            message = f"Запустите асистента с правами администратора..."
            ProgramLog(logger=LOGGER, current_message=message).error_program_log()
            raise PermissionError(message)

        command_to_execute = [
            "!stop_and_remove_service.bat",
        ]

        LOGGER.info(f"Выполняем команды {' '.join(command_to_execute)}")

        try:
            run: subprocess.CompletedProcess = subprocess.run(command_to_execute, capture_output=True)
            if run.returncode == 0:
                LOGGER.info(f"Команды {' '.join(command_to_execute)} выполнены успешно.")
            else:
                LOGGER.error(f"Проблема выполнения команд {' '.join(command_to_execute)}. returncode={run.returncode}")
        except Exception:
            message = "Exception stop_service"
            ProgramLog(logger=LOGGER, current_message=message).error_program_log()
            raise Exception(message)

    def debug_service(self):
        if not pyuac.isUserAdmin():
            message = f"Запустите асистента с правами администратора..."
            ProgramLog(logger=LOGGER, current_message=message).error_program_log()
            raise PermissionError(message)

        command_to_execute = [
            "!debug_service.bat",
        ]

        LOGGER.info(f"Выполняем команды {' '.join(command_to_execute)}")

        try:
            run: subprocess.CompletedProcess = subprocess.run(command_to_execute, capture_output=True)
            if run.returncode == 0:
                LOGGER.info(f"Команды {' '.join(command_to_execute)} выполнены успешно.")
            else:
                LOGGER.error(f"Проблема выполнения команд {' '.join(command_to_execute)}. returncode={run.returncode}")
        except Exception:
            message = "Exception debug_service"
            ProgramLog(logger=LOGGER, current_message=message).error_program_log()
            raise Exception(message)

    def login_event(self, event=None):
        self.error_textbox.delete("0.0", "100.100")
        LOGGER.info("Попытка ввода данных для авторизации")

        # with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        #     futures = []
        #     futures.append(
        #         executor.submit(
        #             ServerAuthorizationV2.renew_token,
        #             api_endpoint=self.api_endpoint_entry.get(),
        #             username=self.username_entry.get(),
        #             password=self.password_entry.get(),
        #             method=TokenSaveMethod.BD,
        #         )
        #     )
        # LOGGER.info(futures)
        # for future in concurrent.futures.as_completed(futures):
        request_result = ServerAuthorizationV2.renew_token(
            api_endpoint=self.api_endpoint_entry.get(),
            username=self.username_entry.get(),
            password=self.password_entry.get(),
            method=TokenSaveMethod.BD)
        if request_result[0] is None:
            self.error_textbox.insert("0.0", request_result[1])
            LOGGER.info(f"Ошибка авторизации. {request_result[1]}")
        else:
            LOGGER.info("Авторизация прошла успешно. Токен записан в БД.")
            authorization_token = request_result[0]
            # Запишем токен авторизации в БД
            DBConnector.save_token(token=authorization_token)
            # self.error_textbox.insert("0.0", authorization_token)

            # Записать часть настроект сервера в таблицу настроек
            WriteSettingsToBD.after_authorization(
                api_endpoint=self.api_endpoint_entry.get(),
                api_login=self.username_entry.get(),
                api_password=self.password_entry.get()
            )

            # Получить настройки асистента с сервера
            settings = GetSettingsFromServer.launch(logger=LOGGER)
            if settings[0] is None:
                self.error_textbox.insert("0.0", settings[1])
            else:
                received_settings = settings[0]
                # Записать настройки асистента
                WriteSettingsToBD.after_read_settings(settings=received_settings)

                # Запускаем сервис

                # Показать GUI окно настроек асистента
                self.login_frame.grid_forget()  # remove login frame
                self.main_frame.grid(row=0, column=0, sticky="nsew", padx=100)

                self.check_windows_service()

    def check_windows_service(self):
        # with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        #     futures = []
        #     futures.append(
        #         executor.submit(
        #             CheckWindowsService.run,
        #             service_name=os.getenv("PRODUCT_NAME_SERVICE", "Some service name"),
        #             app_gui_window_obj=self,
        #         )
        #     )
        #
        #     for future in concurrent.futures.as_completed(futures):
        #         result = future.result()
        #         LOGGER.info(result)
        #         print(f"result={result}")
        thread = threading.Thread(
            target=CheckWindowsService.run,
            kwargs={
                "service_name": os.getenv("PRODUCT_NAME_SERVICE", "Some service name"),
                "app_gui_window_obj": self,
            },
            daemon=False
        )
        thread.start()

    def back_event(self):
        self.main_frame.grid_forget()
        self.login_frame.grid(row=0, column=0, sticky="ns")
        self.username_entry.delete(0, 200)
        self.password_entry.delete(0, 200)

    def quit_window(self):
        # psutil.Process().kill
        self.icon.stop()
        self.destroy()
        p = psutil.Process()
        p.kill()

    def show_window(self):
        self.icon.stop()
        self.protocol('WM_DELETE_WINDOW', self.withdraw_window)
        self.after(0, self.deiconify)

    def withdraw_window(self):
        self.withdraw()
        self.icon = pystray.Icon("name", self.image, "ServerWatcher assistant", self.menu)
        self.icon.run()


if __name__ == '__main__':
    if not pyuac.isUserAdmin():
        raise PermissionError(f"Запустите асистента с правами администратора...")

    try:
        # Проверим, что экземпляр программы был запущен ранее, и если он запущен, то прервем выполнение программы
        gui_process_obj = GuiProcess()
        if gui_process_obj.is_app_process_already_exists():
            raise RuntimeError(
                f"Процесс {gui_process_obj.get_current_process_name()} уже запущен на данном компьютере."
            )

        # исправим временное смещение, если оно ноль на то что в переменных окружения часов
        # (на некоторых серверах не подтягиваются в приложения смещения временной зоны)
        TZImproveForPyInstaller(logger=LOGGER, verbose=True).improve()
        LOGGER.info(" Запуск приложения ".center(100, '-'))
        AppGUI()
    except Exception:
        ProgramLog(logger=LOGGER, current_message=f'Неизвестная ошибка Exception...').error_program_log()
