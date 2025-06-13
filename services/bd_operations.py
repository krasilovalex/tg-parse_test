'''Модуль для взаимодействия с базой данных пользователей'''
import sqlite3
import logging

# Логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseData:
    '''Класс для работы с базой данных пользователей'''

    def __init__(self, db_path):
        self.db_path = db_path
        '''Инициализация подключения к БД'''
        logger.debug('Инициализируем класс и соединение с БД')
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()


    def create_bd_if_not_exists(self) -> None:
        '''Создаёт таблицу, если она не существует'''
        logger.info('Попытка инициализировать/создать БД')
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE,
                    username TEXT,
                    access_hash TEXT
                    
                )
            ''')
            self.connection.commit()
        except Exception as e:
            logger.error(f'Не получается создать БД. Ошибка - {e}')

    def add_in_db(self, user_id: str, username: str, access_hash: str) -> None:
        '''
        Добавляет пользователя в БД.
        Использует INSERT OR IGNORE, чтобы не дублировать записи.
        '''
        logger.info(f'Добавление в БД: {user_id}, username={username}')
        try:
            self.cursor.execute(
                '''INSERT OR IGNORE INTO users_data (user_id, username, access_hash) VALUES (?, ?, ?)''',
                (user_id, username, access_hash)
            )
            self.connection.commit()
        except Exception as e:
            logger.error(f'Не получается добавить {user_id}. Ошибка {e}')
        

    def took_all_data_about_user(self):
        '''
        Извлекает все user_id из БД.
        Возвращает список кортежей вида [(user_id1,), (user_id2,), ...]
        '''
        logger.info('Извлечение всех пользователей из БД')
        try:
            self.cursor.execute('SELECT user_id, username, access_hash FROM users_data')
            users_full_ids = self.cursor.fetchall()
            return users_full_ids
        except Exception as e:
            logger.error(f'Ошибка при извлечении данных: {e}')
            return None

    def close_connection_into_bd(self):
        '''Закрывает соединение с БД'''
        try:
            self.connection.close()
            logger.info('Соединение с БД закрыто')
        except Exception as e:
            logger.error(f'Ошибка при закрытии соединения: {e}')
    
    def get_all_users(self):
        '''
        Возвращает список пользователей в формате, ожидаемом рассылкой.
        '''
        users = self.took_all_data_about_user()
        if users:
            return [{"user_id": row[0], "username": row[1], "access_hash": row[2]} for row in users]
        return []
