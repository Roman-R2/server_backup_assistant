from services_common.common_settings import Settings
from services_gui.gui_logger import GuiLogger

LOGGER = GuiLogger().get_logger()


class GetDefaultServerUrl:

    def _from_file(self):
        """ Вернет строку, содержащуюся в файле для хранения API endpoint по умолчанию. """
        try:
            with Settings.DEFAULT_API_ENDPOINT_FILE.open(mode='r', encoding=Settings.COMMON_ENCODING) as fd:
                return fd.readlines()[0].strip()
        except Exception:

            return ""

    @staticmethod
    def from_file():
        return GetDefaultServerUrl()._from_file()


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
