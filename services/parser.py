from services.bd_operations import BaseData
import logging
from telethon.tl.functions.channels import GetFullChannelRequest


def get_linked_chat(group_link, client):
    
    # Получение информации о канале и проверка на наличие обсуждений
    channel = client.get_entity(group_link)
    full = client(GetFullChannelRequest(channel))

    if not full.full_chat or not full.full_chat.linked_chat_id:
        logging.warning("У Канала нет привязанного чата (обсуждения).")
        return None
    
    # Получаем чат обсуждений
    linked_chat_id = full.full_chat.linked_chat_id
    linked_chat = client.get_entity(linked_chat_id)
    return linked_chat

    
# функция пар


def parse_subs_closed(client, linked_chat, bd, message_limit=200):
    """
    Парсит участников привязанного чата (комментаторов) к каналу.
    Добавляет их в базу данных, если удаётся получить access_hash.
    """
    try:
        commenters = set()
        for msg in client.iter_messages(linked_chat, limit=message_limit):
            if msg.from_id and hasattr(msg.from_id, 'user_id'):
                user_id = str(msg.from_id.user_id)
                if user_id in commenters:
                    continue

                try:
                    sender = msg.sender  # получаем готовый объект без get_entity
                    if sender is None or sender.bot:
                        continue

                    username = sender.username or ''
                    access_hash = str(sender.access_hash) if hasattr(sender, 'access_hash') else ''

                    # добавляем только если есть access_hash
                    if access_hash:
                        bd.add_in_db(user_id, username, access_hash)
                        logging.info(f"Добавлен комментатор: {username} ({user_id}) {access_hash}")
                        commenters.add(user_id)
                    else:
                        logging.warning(f"Пропущен {user_id}: нет access_hash")

                except Exception as e:
                    logging.error(f"Не удалось добавить пользователя {user_id}: {e}")

        logging.info(f"Всего добавлено {len(commenters)} комментаторов.")

    except Exception as e:
        logging.error(f"Ошибка при парсинге комментариев: {e}")


def parse_open_subs(client, group_link, bd):
    """
    Парсит участников открытой группы.
    Добавляет их в базу данных.
    """
    group = client.get_entity(group_link)
    participants = client.get_participants(group, aggressive=True)
    logging.info(f"Найдено {len(participants)} участников в {group_link}")

    for user in participants:
        if user.bot or not user.username:
            logging.debug(f"Пропущен: {user.id}")
            continue

        user_id = str(user.id)
        access_hash = str(user.access_hash)
        username = user.username or ''
        try:
            bd.add_in_db(user_id, username, access_hash)
            logging.info(f"Добавлен в БД: {user.username} ({user_id}) {access_hash}")
        except Exception as e:
            logging.error(f"Ошибка при добавлении пользователя {user_id}")

