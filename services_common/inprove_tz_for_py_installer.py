import os
import time
from logging import Logger

from services_common.common_settings import Settings


class TZImproveForPyInstaller:
    def __init__(self, logger: Logger, verbose=False):
        self.logger = logger
        self.local_time = time.localtime()
        if self.local_time.tm_isdst == 0:
            self.tz_offset = time.timezone
        else:
            self.tz_offset = time.altzone

        if verbose:
            self.logger.info(
                f"Системное время: "
                f"\n\tГод: {self.local_time.tm_year}"
                f"\n\tМесяц: {self.local_time.tm_mon}"
                f"\n\tДень: {self.local_time.tm_mday}"
                f"\n\tЧасов: {self.local_time.tm_hour}"
                f"\n\tМинут: {self.local_time.tm_min}"
                f"\n\tСекунд: {self.local_time.tm_sec}"
                f"\n\tДень недели [0, 6], Понедельник это 0: {self.local_time.tm_wday}"
                f"\n\tДень года [1, 366]: {self.local_time.tm_yday}"
                f"\n\t1, если действует летнее время, 0, если нет, и -1, если неизвестно: {self.local_time.tm_isdst}"
                f"\n\tСистемное смещение UTC: {self.tz_offset}"
            )

    def improve(self):
        if self.tz_offset == 0:
            self.logger.info(f"Так как {self.tz_offset=} исправляем UTC смещение на {Settings.OS_ENVIRON_TZ}")
            os.environ['TZ'] = Settings.OS_ENVIRON_TZ
