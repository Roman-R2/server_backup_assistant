import os

import pyinstaller_versionfile
from dotenv import load_dotenv

from services_common.common_settings import Settings

load_dotenv(Settings.BASE_DIR / '.env')

gui_versionfile_path = Settings.BASE_DIR / "app-build" / "gui" / os.getenv('VERSIONFILE_GUI_NAME')
service_versionfile_path = Settings.BASE_DIR / "app-build" / "service" / os.getenv('VERSIONFILE_SERVICE_NAME')

print(gui_versionfile_path)

# Create versionfile for R2ZiD server assistant GUI
pyinstaller_versionfile.create_versionfile(
    output_file=gui_versionfile_path,
    version=os.getenv("ASSISTANT_VERSION"),
    company_name="",
    file_description=os.getenv('PRODUCT_NAME_GUI'),
    internal_name=os.getenv('PRODUCT_NAME_GUI'),
    legal_copyright="",
    original_filename=f"{os.getenv('ASSISTANT_NAME_GUI')}.exe",
    product_name=os.getenv('PRODUCT_NAME_GUI')
)

print(f"Файл версия для {os.getenv('PRODUCT_NAME_GUI')} создан. {gui_versionfile_path}")

# Create versionfile for R2ZiD server assistant win service
pyinstaller_versionfile.create_versionfile(
    output_file=service_versionfile_path,
    version=os.getenv("ASSISTANT_VERSION"),
    company_name="",
    file_description=os.getenv('PRODUCT_NAME_SERVICE'),
    internal_name=os.getenv('PRODUCT_NAME_SERVICE'),
    legal_copyright="",
    original_filename=f"{os.getenv('ASSISTANT_NAME_SERVICE')}.exe",
    product_name=os.getenv('PRODUCT_NAME_SERVICE')
)

print(f"Файл версия для {os.getenv('PRODUCT_NAME_SERVICE')} создан. {service_versionfile_path}")
