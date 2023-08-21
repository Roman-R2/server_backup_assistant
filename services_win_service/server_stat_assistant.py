import platform
import re
import socket
import uuid
from typing import List
from winreg import (HKEY_LOCAL_MACHINE, EnumKey, EnumValue, OpenKey,
                    QueryInfoKey)

import psutil

from services_common.dto import ServerStatDTO, PhysicalDiskDTO, InstalledProgramDTO
from services_win_service.service_logger import ServiceLogger

LOGGER = ServiceLogger().get_logger()


class ServerWinStatAssistant:
    """
    Класс соберет статистику по компьютеру и вернет ее в виде ServerStatDTO.
    """
    UNINSTALL_PATH_LIST = [
        r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
        r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]

    def __init__(self, assistant_auth_token: str) -> None:
        self.assistant_auth_token = assistant_auth_token

    def get_statistics(self) -> ServerStatDTO:
        server_stat = ServerStatDTO(
            token=self.assistant_auth_token,
            platform=platform.system(),
            platform_release=platform.release(),
            platform_version=platform.version(),
            architecture=platform.machine(),
            hostname=socket.gethostname(),
            ip_address=socket.gethostbyname(socket.gethostname()),
            mac_address=':'.join(re.findall('..', '%012x' % uuid.getnode())),
            processor=platform.processor(),
            physical_memory=psutil.virtual_memory(),
            swap_memory=psutil.swap_memory(),
            disks=self.__get_recording_devices_stat(),
            installed_programs=self.__get_installed_programs(),
        )
        LOGGER.info(f'Собрана статистика по серверу {server_stat.hostname} ({server_stat.platform_release})')
        return server_stat

    def __get_recording_devices_stat(self) -> List[PhysicalDiskDTO]:
        """ Получит данные только о физических устройствах """
        recording_devices_data = []
        for device in psutil.disk_partitions(all=False):
            try:
                disk_usage = psutil.disk_usage(device.device)
                recording_devices_data.append(
                    PhysicalDiskDTO(
                        device=device.device,
                        mountpoint=device.mountpoint,
                        fstype=device.fstype,
                        opts=device.opts,
                        maxfile=device.maxfile,
                        maxpath=device.maxpath,
                        total=disk_usage.total,
                        used=disk_usage.used,
                        free=disk_usage.free,
                        percent=disk_usage.percent,
                    )
                )
            except PermissionError as error:
                LOGGER.error(f"Ошибка при чтении информации о физических дисках: {error}")
                continue
        return recording_devices_data

    def __get_installed_programs(self) -> List[InstalledProgramDTO]:
        """ Вернет список установленных программ в ОС Windows """
        programs = []

        for path in self.UNINSTALL_PATH_LIST:
            with OpenKey(HKEY_LOCAL_MACHINE, path) as key:
                for i in range(QueryInfoKey(key)[0]):
                    keyname = EnumKey(key, i)
                    subkey = OpenKey(key, keyname)

                    try:
                        subkey_dict = dict()
                        for j in range(QueryInfoKey(subkey)[1]):
                            k, v = EnumValue(subkey, j)[:2]
                            subkey_dict[k] = v

                        if 'DisplayName' not in subkey_dict:
                            continue

                        name = subkey_dict['DisplayName'].strip()
                        if not name:
                            continue

                        programs.append(
                            InstalledProgramDTO(
                                display_name=subkey_dict['DisplayName'] if 'DisplayName' in subkey_dict else '',
                                display_version=subkey_dict[
                                    'DisplayVersion'] if 'DisplayVersion' in subkey_dict else '',
                                install_location=subkey_dict[
                                    'InstallLocation'] if 'InstallLocation' in subkey_dict else '',
                            )
                        )

                    except WindowsError:
                        pass
            return programs


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
