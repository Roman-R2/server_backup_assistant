from services_common.common_logger import CustomLogger
from services_common.common_settings import Settings


class GuiLogger(CustomLogger):
    logger_file = Settings.GUI_LOG_FILE

    def __init__(self):
        super().__init__(logger_name=Settings.GUI_LOGGER_NAME)


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
