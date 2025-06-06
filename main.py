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

from utils.utils import load_group_links, autorization_tg
from parsers.parsers_open import parse_open_subs
from parsers.parsers_closed import parse_subs_closed

import asyncio
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    handlers=[
        logging.FileHandler('parse_test_log.txt'),
        logging.StreamHandler()
    ]
)
# функция парса по комментам
def main():
    """
    Основная функция запуска парсинга. группы хранятся в groups.txt
    """
    
    
    logging.info("Запуска парсера")
    bd = BaseData()
    bd.create_bd_if_not_exists()
    client = autorization_tg()
    logging.info(f"Подключено как: {client.get_me().username}")
    users = bd.took_all_data_about_user()
    logging.info(f"Содержимое БД: {users}")
    group_links = load_group_links()

    for link in group_links:
        try:
        # Чекаем есть ли чат
            channel = client.get_entity(link)
            full = client(GetFullChannelRequest(channel=channel))
            if full.full_chat and full.full_chat.linked_chat_id:
                parse_subs_closed(link, client, bd)
            else:
                parse_open_subs(link, client, bd)
        except Exception as e:
            logging.error(f"Ошибка при обработке {link}: {e}")

    bd.close_connection_into_bd()
    client.disconnect
    logging.info('Готово!')

if __name__ == '__main__':
    main()