import os
import shutil
import time

import pyuac

from distutils.dir_util import copy_tree
from dotenv import load_dotenv
from services_common.common_settings import Settings

load_dotenv(Settings.BASE_DIR / '.env')

gui_compiled_folder = Settings.BASE_DIR / 'app-build' / 'gui' / 'dist' / os.getenv("ASSISTANT_NAME_GUI")
service_compiled_folder = Settings.BASE_DIR / 'app-build' / 'service' / 'dist' / os.getenv("ASSISTANT_NAME_SERVICE")
folder_for_add = Settings.BASE_DIR / 'app-build' / 'compile-app'
txt_version_file = Settings.BASE_DIR / "!app-version.txt"

if not pyuac.isUserAdmin():
    pyuac.runAsAdmin()
else:
    # Копируем скомпилированную программу для GUI
    copy_tree(str(gui_compiled_folder), str(folder_for_add))
    print("Скопировали скомпилированную программу для GUI")
    # Копируем скомпилированную программу для service
    copy_tree(str(service_compiled_folder), str(folder_for_add))
    print("Скопировали скомпилированную программу для service")
    shutil.copy2(txt_version_file, folder_for_add)
    print("Скопировали файл версии в папку с итоговой программой")
    # Переименовываем папку с итоговой программой
    os.rename(
        Settings.BASE_DIR / 'app-build' / 'compile-app',
        Settings.BASE_DIR / 'app-build' / os.getenv("ASSISTANT_COMMON_NAME")
    )
    print("Переименовали папку с итоговой программой")
    time.sleep(5)
