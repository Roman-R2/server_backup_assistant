import os
from pathlib import Path

import chardet
from dotenv import load_dotenv
from win32api import GetFileVersionInfo, HIWORD, LOWORD

from services_common.common_settings import Settings
from services_common.db_connector import DBConnector

load_dotenv(Settings.BASE_DIR / '.env')


# def get_hashed_password(plain_text_password):
#     # Hash a password for the first time
#     #   (Using bcrypt, the salt is saved into the hash itself)
#     return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())
#
# def check_password(plain_text_password, hashed_password):
#     # Check hashed password. Using bcrypt, the salt is saved into the hash itself
#     return bcrypt.checkpw(plain_text_password, hashed_password)


class JsonHeaderMixin:
    def __init__(self):
        super().__init__()
        try:
            self.headers.update({'Content-type': 'application/json'})
        except Exception:
            self.headers = {}
            self.headers.update({'Content-type': 'application/json'})


class AddTokenToHeaderMixin:
    def __init__(self):
        super().__init__()
        self.token = DBConnector.get_token()
        try:
            self.headers.update({'Authorization': f'Token {self.token}'})
        except Exception:
            self.headers = {}
            self.headers.update({'Authorization': f'Token {self.token}'})


def get_file_encoding(path_to_file: Path):
    """ Возможно вернет кодировку файла. """
    with open(path_to_file, 'rb') as fd:
        file_bytes_line = fd.read(50)
    return chardet.detect(file_bytes_line)['encoding']


def get_service_exe_version_number(file_path: str = None):
    if file_path is None:
        file_path = str(Settings.BASE_DIR / f"{os.getenv('ASSISTANT_NAME_SERVICE')}.exe")

    print(f"file_path={file_path}")

    file_information = GetFileVersionInfo(file_path, "\\")

    ms_file_version = file_information['FileVersionMS']
    ls_file_version = file_information['FileVersionLS']

    return ".".join([
        str(HIWORD(ms_file_version)),
        str(LOWORD(ms_file_version)),
        str(HIWORD(ls_file_version)),
        str(LOWORD(ls_file_version))
    ])
