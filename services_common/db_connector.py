from sqlalchemy import create_engine, Column, Integer, String, delete, update, Boolean, inspect, MetaData, insert
from sqlalchemy.orm import DeclarativeBase, Session

from services_common.common_settings import Settings
from services_common.dto import UnitForScanDTO


class Base(DeclarativeBase):
    pass


class DBSettings(Base):
    """ Таблица настроек асистента. """
    __tablename__ = 'Settings'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    api_endpoint = Column(String, nullable=False, unique=True)
    api_login = Column(String, nullable=False)
    api_password = Column(String, nullable=False)
    assistant_server_ip = Column(String, nullable=False, default='127.0.0.1')
    backup_sending_minutes_frequency = Column(Integer, nullable=False, default=60)
    stat_sending_minutes_frequency = Column(Integer, nullable=False, default=10)
    precision_sending_minutes_frequency = Column(Integer, nullable=False, default=1)
    ask_settings_minutes_frequency = Column(Integer, nullable=False, default=1)
    is_new_settings = Column(Boolean, nullable=False, default=0)


class DBBackupFolders(Base):
    """ Таблица настроек асистента. """
    __tablename__ = 'Backup_folders'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    folder_path = Column(String, nullable=False, unique=True)
    reqexp_pattern = Column(String, nullable=False)
    allowed_file_formats = Column(String, nullable=False)


class DBBackupTSMLogFiles(Base):
    """ Таблица настроек для файлов логирования бэкапов от TSM. """
    __tablename__ = 'Backup_tsm_log'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    log_file_name = Column(String, nullable=False)
    path_to_log_file = Column(String, nullable=False, unique=True)


class DBTokens(Base):
    """ Таблица хранения токена. """
    __tablename__ = 'Tokens'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    token = Column(String, nullable=False, unique=True)


class DBConnector:
    """ Основной класс, котороый работает с БД. """

    scheme_tables_names = [
        DBTokens,
        DBBackupFolders,
        DBBackupTSMLogFiles,
        DBSettings
    ]

    def __init__(self):
        self.engine = create_engine(f"sqlite:///{Settings.SQLITE3_DATABASE_FILE}")
        self.meta = MetaData()

        # Создадим таблицы, если их нет в БД или не было самой БД
        for table in self.scheme_tables_names:
            if not inspect(self.engine).has_table(table.__tablename__):
                table.__table__.create(bind=self.engine, checkfirst=True)
                message = f"Таблица {table.__tablename__} создана."
                print(message)
                # LOGGER.info(message)

    def write_data_after_authorization(self, api_endpoint, api_login, api_password):
        """ Добавит часть известных данных в таблице настроек после авторизации асистента на сервере-наблюдателе. """
        with Session(self.engine) as session:
            current_settings = self.read_common_settings()
            # print(f"{current_settings=}")
            stmt = (
                update(DBSettings).
                where(DBSettings.id == current_settings.id).
                values(
                    api_endpoint=api_endpoint,
                    api_login=api_login,
                    api_password=api_password
                )
            )
            session.execute(stmt)
            session.commit()

    def _get_token(self):
        """ Получит токен из базы данных. """
        with Session(self.engine) as session:
            result = session.query(DBTokens).first()
            if result is None:
                return ""
            else:
                return result.token

    @staticmethod
    def get_settings_label():
        """ Поставит метку об обновлении настроек. """
        return DBConnector()._get_settings_label()

    def _get_settings_label(self):
        """ Получит метку об обновлении настроек. """
        with Session(self.engine) as session:
            result = session.query(DBSettings).first()
            if result is None:
                return ""
            else:
                return result.is_new_settings

    @staticmethod
    def label_the_new_settings(label=False):
        """ Поставит метку об обновлении настроек. """
        return DBConnector()._label_the_new_settings(label=label)

    def _label_the_new_settings(self, label=False):
        current_settings = self.read_common_settings()
        with Session(self.engine) as session:
            stmt = (
                update(DBSettings).
                where(DBSettings.id == current_settings.id).
                values(
                    is_new_settings=label,
                )
            )
            session.execute(stmt)
            session.commit()

    @staticmethod
    def get_token():
        return DBConnector()._get_token()

    def _get_username(self):
        """ Получит токен из базы данных. """
        with Session(self.engine) as session:
            result = session.query(DBSettings).first()
            if result:
                return result.api_login
            else:
                return ""

    @staticmethod
    def get_username():
        return DBConnector()._get_username()

    def _get_password(self):
        """ Получит токен из базы данных. """
        with Session(self.engine) as session:
            result = session.query(DBSettings).first()
            if result:
                return result.api_password
            else:
                return ""

    @staticmethod
    def get_password():
        return DBConnector()._get_password()

    def _save_token(self, token):
        """ Обновит токен в таблице БД, сначала все удалив, а затем добавив запись. """
        with Session(self.engine) as session:
            stmt = (delete(DBTokens))
            session.execute(stmt)
            session.commit()

            new_token_record = DBTokens(token=token)
            session.add(new_token_record)
            session.commit()

    @staticmethod
    def save_token(token):
        return DBConnector()._save_token(token=token)

    def read_backup_tsm_log_settings(self) -> list:
        """ Получит данные из таблицы по настройкам лог файлов бэкапов TSM. """
        with Session(self.engine) as session:
            result = session.query(DBBackupTSMLogFiles).all()
            return result

    def read_backup_settings(self) -> list:
        """ Получит данные из таблицы по настройкам бэкапов. """
        with Session(self.engine) as session:
            result = session.query(DBBackupFolders).all()
            return result

    def read_common_settings(self):
        """ Получит данные из таблицы по общим настройкам ассистента. """
        with Session(self.engine) as session:
            result = session.query(DBSettings).first()
            if result is None:
                stmt = (
                    insert(DBSettings).
                    values(
                        api_endpoint="",
                        api_login="",
                        api_password="",
                    )
                )
                session.execute(stmt)
                session.commit()
                return session.query(DBSettings).first()
            return result

    def _write_data_after_read_settings(
            self,
            backup_sending_minutes_frequency,
            stat_sending_minutes_frequency,
            precision_sending_minutes_frequency,
            ask_settings_minutes_frequency,
            backup_folders,
            backup_tsm_log_files
    ):
        """ Запишет данные в таблицу по общим настройкам ассистента. """
        with Session(self.engine) as session:
            # Запишем общие настройки
            current_settings = self.read_common_settings()
            stmt = (
                update(DBSettings).
                where(DBSettings.id == current_settings.id).
                values(
                    backup_sending_minutes_frequency=backup_sending_minutes_frequency,
                    stat_sending_minutes_frequency=stat_sending_minutes_frequency,
                    precision_sending_minutes_frequency=precision_sending_minutes_frequency,
                    ask_settings_minutes_frequency=ask_settings_minutes_frequency,
                )
            )
            session.execute(stmt)
            session.commit()

            # Удалим все настройки по бэкапам из таблицы в локальной БД
            session.query(DBBackupFolders).delete()
            session.commit()

            # Удалим все настройки по TSM файлам логов из таблицы в локальной БД
            session.query(DBBackupTSMLogFiles).delete()
            session.commit()

            # Запишем настройки по бэкапам из полученных данных с сервера-наблюдателя
            for backup_item in backup_folders:
                backup_item: UnitForScanDTO = backup_item
                stmt = (
                    insert(DBBackupFolders).
                    values(
                        folder_path=str(backup_item.folder_path.absolute()),
                        reqexp_pattern=backup_item.reqexp_pattern,
                        allowed_file_formats=",".join(backup_item.allowed_file_formats),
                    )
                )
                session.execute(stmt)

            for tsm_log_item in backup_tsm_log_files:
                tsm_log_item: DBBackupTSMLogFiles = tsm_log_item
                stmt = (
                    insert(DBBackupTSMLogFiles).
                    values(
                        log_file_name=tsm_log_item.log_file_name,
                        path_to_log_file=str(tsm_log_item.path_to_log_file.absolute()),
                    )
                )
                session.execute(stmt)
            session.commit()

    @staticmethod
    def write_data_after_read_settings(
            backup_sending_minutes_frequency,
            stat_sending_minutes_frequency,
            precision_sending_minutes_frequency,
            ask_settings_minutes_frequency,
            backup_folders,
            backup_tsm_log_files
    ):
        return DBConnector()._write_data_after_read_settings(
            backup_sending_minutes_frequency,
            stat_sending_minutes_frequency,
            precision_sending_minutes_frequency,
            ask_settings_minutes_frequency,
            backup_folders,
            backup_tsm_log_files
        )

    def _read_api_endpoint(self):
        with Session(self.engine) as session:
            result = session.query(DBSettings).first()
            if result is None:
                return None
            return result.api_endpoint

    @staticmethod
    def read_api_endpoint():
        return DBConnector()._read_api_endpoint()


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
