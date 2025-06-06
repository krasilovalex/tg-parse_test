
import logging
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import PeerChannel
from telethon.errors import SessionPasswordNeededError
from dotenv import load_dotenv
import os


load_dotenv()

# api из .env
phone_number = os.getenv('PHONE_NUMBER')
password = os.getenv('PASSWORD')
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
system_version = os.getenv("SYSTEM_VERSION", 'Unknown OS')
device_model = os.getenv('DEVICE_MODEL', 'Pc Club')

session_name = 'anon'

# функция загрузки файла .txt

def load_group_links(filepath='./data/groups.txt'):
    """
    Загружает список ссылок на группы из текстового файла.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            links = [line.strip() for line in f if line.strip()]
        logging.info(f"Загружено {len(links)} групп из {filepath}")
        return links
    except Exception as e:
        logging.error(f"Не удалось загрузить список групп : {e}")
        return []



def autorization_tg():
    """
    Авторизация в Telegram-клиенте.
    Возвращает авторизованный клиент.
    """
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