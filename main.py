from bd.bd_operations import BaseData
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import PeerChannel
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetDiscussionMessageRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetMessagesRequest
import asyncio
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    handlers=[
        logging.FileHandler('scan-matrix-log.txt'),
        logging.StreamHandler()
    ]
)


load_dotenv()

# api из .env
phone_number = os.getenv('PHONE_NUMBER')
password = os.getenv('PASSWORD')
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
system_version = os.getenv("SYSTEM_VERSION", 'Unknown OS')
device_model = os.getenv('DEVICE_MODEL', 'Pc Club')

session_name = 'anon'

# функция авторизации
def autorization_tg():
    logging.info(f"Авторизация под номером телефона {phone_number}")
    client = TelegramClient(
        session_name,
        api_id,
        api_hash,
        device_model=device_model,
        system_version=system_version
    )

    client.connect()

    if not client.is_user_authorized():
        client.send_code_request(phone_number)
        code = input('Введите код из Telegram: ')

        try:
            client.sign_in(phone_number, code)
        except SessionPasswordNeededError:
            logging.info("Нужен пароль: у аккаунта включена 2FA")
            client.sign_in(password=password)

    return client



# функция парса открытой группы
def parse_subs(group_link, client):
    bd = BaseData()
    bd.create_bd_if_not_exists()

    logging.info(f"Подключено как: {client.get_me().username}")

    
    group = client.get_entity(group_link)
    participants = client.get_participants(group, aggressive=True)
    logging.info(f"Найдено {len(participants)} участников в {group_link}")

    for user in participants:
        if user.bot or not user.username:
            logging.debug(f"Пропущен: {user.id}")
            continue

        user_id = str(user.id)
        bd.add_in_db(user_id)
        logging.info(f"Добавлен в БД: {user.username} ({user_id})")

    user_id = str(user.id)
    bd.add_in_db(user.id)
    logging.info(f"Добавлен к БД: {user.username} ({user_id})")
    
    bd.close_connection_into_bd()
    client.disconnect()
    logging.info(f"Завершено: соединение закрыто... :(")

# функция парса по комментам

def parse_subs_closed(group_link, client, bd, message_limit=200):
    try:
        logging.info(f"Парсим комментаторов из: {group_link}")

        # Получаем сущность канала и полную информацию
        channel = client.get_entity(group_link)
        full = client(GetFullChannelRequest(channel=channel))

        if not full.full_chat or not full.full_chat.linked_chat_id:
            logging.warning("У канала нет привязанного чата (обсуждения).")
            return

        # Получаем привязанный чат
        linked_chat_id = full.full_chat.linked_chat_id
        linked_chat = client.get_entity(PeerChannel(linked_chat_id))
        logging.info(f"Найден обсуждаемый чат: {linked_chat.title}")

        commenters = set()

        # Используем iter_messages для гибкости
        for msg in client.iter_messages(linked_chat, limit=message_limit):
            if msg.from_id and hasattr(msg.from_id, 'user_id'):
                uid = str(msg.from_id.user_id)
                if uid not in commenters:
                    try:
                        bd.add_in_db(uid)
                        logging.info(f"Добавлен комментатор: {uid}")
                    except Exception as e:
                        logging.error(f"Не удалось добавить {uid}. Ошибка: {e}")
                    commenters.add(uid)

        logging.info(f"Всего добавлено {len(commenters)} комментаторов.")

    except Exception as e:
        logging.error(f"Ошибка при парсинге комментариев: {e}")
def main():
    
    logging.info("Запуска парсера")
    bd = BaseData()
    bd.create_bd_if_not_exists()
    client = autorization_tg()
    logging.info(f"Подключено как: {client.get_me().username}")
    bd.add_in_db('51511515135')
    bd.add_in_db('5123412312')
    users = bd.took_all_data_about_user()
    logging.info(f"Содержимое БД: {users}")
   
    parse_subs('https://t.me/giftsuppliers',client)
    parse_subs_closed('https://t.me/presentica', client, bd)


    bd.close_connection_into_bd()
    logging.info('Готово!')

if __name__ == '__main__':
    main()