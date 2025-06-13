
import logging
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
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




from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
import logging


def authorize(client_data: dict) -> TelegramClient:
    """
    Авторизация клиента Telegram через Telethon с автоматическим стартом.
    """
    logging.info(f"Аутентификация: {client_data['session_name']} ({client_data['phone_number']})")

    client = TelegramClient(
        client_data['session_name'],
        client_data['api_id'],
        client_data['api_hash'],
        device_model=client_data.get('device_model', 'PC'),
        system_version=client_data.get('system_version', 'Windows 10')
    )

    try:
        client.start(
            phone=client_data['phone_number'],
            password=client_data.get('password')  # Если 2FA, иначе None
        )
    except Exception as e:
        logging.error(f"Ошибка авторизации: {e}")
        raise

    return client


def save_message(msg: str):
    with open("message.txt", "w", encoding="utf-8") as f:
        f.write(msg)

def load_messages() -> str:
    try:
        with open("message.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""
