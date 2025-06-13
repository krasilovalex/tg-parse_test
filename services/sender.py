import time
import logging
from telethon.sync import TelegramClient
from services.bd_operations import BaseData  
from telethon.tl.types import InputPeerUser

from utils.utils import load_messages


def send_invites(client: TelegramClient, bd: BaseData, delay: int = 10):
    """
    Отправляет сообщение каждому пользователю из БД.
    """
    message = load_messages()

    if not message:
        logging.warning("Пустое сообщение...")
        return

    users = bd.took_all_data_about_user()

    logging.info(f"Начинается рассылка {len(users)} пользователям")

    for row in users:
        user_id, username, access_hash = row
        try:
            entity = InputPeerUser(int(user_id), int(access_hash))
            client.send_message(entity, message)
            logging.info(f"Сообщение отправлено пользователю {username} ({user_id})")
            time.sleep(delay)
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения {user_id}: {e}")

    logging.info("Рассылка завершена")

    