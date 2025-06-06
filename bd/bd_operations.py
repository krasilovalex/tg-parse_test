'''Модуль для взаимодействия с бд'''
import sqlite3
import logging

#logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseData:
    '''Класс для взаимодействия с бд'''
    def __init__(self):
        logger.debug('Инициализируем класс')
        self.connection = sqlite3.connect('users.db', check_same_thread=False)
        self.cursor = self.connection.cursor()

    def create_bd_if_not_exists(self) -> None:
        '''Создание бд, если дубликат - ничего не делает'''
        logger.info('Попытка инициализировать/создать бд')
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS users_data(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT
            )''')
        except Exception as e:
            logger.error(f'Не получается создать бд. Ошибка - {e}')
        self.connection.commit()

    def add_in_db(self, user_id:str) -> None:
        '''Добавление в бд'''
        logger.info(f'Запускаем добавление {user_id}')
        try:
            self.cursor.execute('''INSERT OR IGNORE INTO users_data(user_id) VALUES (?)''', (user_id,))
            self.connection.commit()
        except Exception as e:
            logger.error(f'Не получается добавить {user_id}. Ошибка {e}')

    def took_all_data_about_user(self):
        '''Захват всех данных с бд'''
        logger.info('Запускаем сбор всех юзеров')
        try:
            self.cursor.execute('SELECT user_id FROM users_data')
            users_full_ids = self.cursor.fetchall()
        except Exception as e:
            logger.error(f'Не получается схватить всех юзеров. Ошибка {e}')
            return None
        return users_full_ids

    def close_connection_into_bd(self):
        '''Закрыть коннект к бд'''
        try:
            self.connection.close()
            logger.info('Коннект к бд закончен')
        except Exception as e:
            logger.error(f'Ошибка при закрытии бд. {e}')