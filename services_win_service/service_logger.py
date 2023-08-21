from services_common.common_logger import CustomLogger
from services_common.common_settings import Settings


class ServiceLogger(CustomLogger):
    logger_file = Settings.SERVICE_LOG_FILE

    def __init__(self):
        super().__init__(logger_name=Settings.SERVICE_LOGGER_NAME)
