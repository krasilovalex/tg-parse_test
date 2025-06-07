from bd.bd_operations import BaseData
import logging
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import PeerChannel


def get_linked_chat(group_link, client, bd):
    
    # Получение информации о канале и проверка на наличие обсуждений
    channel = client.get_entity(group_link)
    full = client(GetFullChannelRequest)

    if not full.full_chat or not full.full_chat.linked_chat_id:
        logging.warning("У Канала нет привязанного чата (обсуждения).")
        return
    
    # Получаем чат обсуждений
    linked_chat_id = full.full_chat.linked_chat_id
    linked_chat = client.get_entity(PeerChannel(linked_chat_id))
    logging.info(f"Найден обсуждаемый чат : {linked_chat.title}")

    commenters = set()
    
# функция пар


def parse_subs_closed(client,commenters, linked_chat, bd, message_limit=200, ):
    """
    Парсит участников привязанного чата (комментаторов) к каналу.
    Добавляет их в базу данных.
    """
    try:
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
