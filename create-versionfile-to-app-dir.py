""" Добавит файл !app-version.txt в корень папки с программой. """
import os
import time

from dotenv import load_dotenv

from services_common.common_settings import Settings

load_dotenv(Settings.BASE_DIR / '.env')

txt_versionfile_name = '!app-version.txt'
win_service_version = os.getenv('ASSISTANT_VERSION', '0.0.0.0')

with open(Settings.BASE_DIR / txt_versionfile_name, mode='w', encoding=Settings.COMMON_ENCODING) as fd:
    fd.write(win_service_version)

print(f"Создали файл {txt_versionfile_name} с номером версии программы. ")
time.sleep(5)
