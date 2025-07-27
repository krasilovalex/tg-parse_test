import logging
from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import SendMessageRequest
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError
from telethon.tl.types import InputPeerUser
from services.bd_operations import BaseData
from aiogram.types import Message
from utils.utils import load_messages
from core.client import get_telethon_client
import asyncio


async def run_parser(group_links, client=None, db_path='users.db'):
    """
    Парсит несколько групп подряд.
    :param group_links: список ссылок на группы или одна ссылка (str или list)
    :param client: Telethon клиент (если None — создаст сам)
    :return: dict {group_link: count или статус}
    """
    bd = BaseData(db_path)

    bd.create_bd_if_not_exists()

    if isinstance(group_links, str):
        group_links = [group_links]

    own_client = False  # <== флаг, создавали ли мы клиента

    if client is None:
        client = await get_telethon_client(prefix="PARSER", default_session="sessions/parser.session")
        own_client = True

    if client == "AUTH_REQUIRED":
        return "AUTH_REQUIRED"
    elif client is None:
        logging.error("Не удалось получить Telethon клиента")
        return {}

    results = {}

    for group_link in group_links:
        try:
            count = await parse_open_subs_async(client, group_link, bd)
            results[group_link] = count
        except Exception as e_open:
            logging.warning(f"parse_open_subs_async не сработал для {group_link}: {e_open}. Пытаемся закрытый парсер...")
            try:
                count = await parse_closed_subs_async(client, group_link, bd)
                results[group_link] = count
            except Exception as e_closed:
                logging.error(f"parse_closed_subs_async тоже не сработал для {group_link}: {e_closed}")
                results[group_link] = f"Ошибка: {e_closed}"

    if own_client and client.is_connected():
        await client.disconnect()

    return results



async def parse_open_subs_async(client, group_link, bd) -> int:
    """
    Асинхронная версия парсинга открытого канала.
    """
    logging.info(f"Начинаем парсинг открытого канала : {group_link}")
    group = await client.get_entity(group_link)
    participants = await client.get_participants(group, aggressive=True)
    logging.info(f"Найдено {len(participants)} участников в {group_link}")

    count = 0
    for user in participants:
        if user.bot or not user.username:
            username =  user.username or ''
            bd.add_in_db(user_id, username, access_hash)
        
        user_id = str(user.id)
        access_hash = str(user.access_hash)
        username = user.username or ''

        try:
            bd.add_in_db(user_id, username, access_hash)
            logging.info(f"Добавлен в БД: {username} ({user_id} {access_hash})")
            count += 1
        except Exception as e:
            logging.error(f"Ошибка при добавлениии пользователя {user_id}")

    return count

async def parse_closed_subs_async(client, group_link, bd, message_limit=1000) -> int:
    """
    Асинхронная версия парсинга по комментам (закрытый чат).
    """
    logging.info(f"Начинаем парсинг закрытого обсуждения для: {group_link}")

    #Получаем linked_chat
    channel = await client.get_entity(group_link)
    full = await client(GetFullChannelRequest(channel))
    if not full.full_chat or not full.full_chat.linked_chat_id:
        logging.warning("У канала нет привязанного чата(обсуждения)")
        return 0

    linked_chat_id = full.full_chat.linked_chat_id
    linked_chat = await client.get_entity(linked_chat_id)

    commenters = set()

    async for msg in client.iter_messages(linked_chat, limit=message_limit):
        if msg.from_id and hasattr(msg.from_id, 'user_id'):
            user_id = str(msg.from_id.user_id)
            if user_id in commenters:
                continue

            try:
                sender = msg.sender
                if sender is None or sender.bot:
                    continue

                username = sender.username or ''
                access_hash = str(sender.access_hash) if hasattr(sender, 'access_hash') else ''

                if access_hash:
                    bd.add_in_db(user_id, username, access_hash)
                    logging.info(f"Добавлен комментатор: {username} ({user_id} {access_hash})")
                    commenters.add(user_id)
                else:
                    logging.warning(f"Пропущен: {user_id}: нет access_hash")
            except Exception as e:
                logging.error(f"Не удалось добавить пользователя {user_id}: {e}")
    logging.info(f"Всего добавлено {len(commenters)} комментаторов")
    return len(commenters)


async def send_invites(client: TelegramClient, bd: BaseData, message_text: str, delay: int = 10):
    """
    Отправляет сообщение каждому пользователю из БД.
    """
    users = bd.took_all_data_about_user()

    logging.info(f"Начинается рассылка {len(users)} пользователям")

    for row in users:
        user_id, username, access_hash = row
        try:
            entity = InputPeerUser(int(user_id), int(access_hash))
            await client.send_message(entity, message_text)
            logging.info(f"Сообщение отправлено пользователя {username}")
            await asyncio.sleep(delay)  # <== здесь асинхронный sleep вместо time.sleep
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения {user_id} : {e}")

    logging.info("Рассылка завершена")

async def run_sender(client, bd, message_text: str):
    try:
        await client.connect()
        if not await client.is_user_authorized():
            logging.error("❌ Клиент не авторизован!")
            return

        users = bd.get_all_users()
        logging.info(f"Начинаем рассылку {len(users)} пользователям.")

        success_count = 0
        fail_count = 0

        for user in users:
            user_id = user.get("user_id")
            if not user_id:
                continue
            try:
                await client(SendMessageRequest(
                    peer=int(user_id),
                    message=message_text,
                    no_webpage=True
                ))
                logging.info(f"✅ Сообщение отправлено пользователю {user_id}")
                success_count += 1
                await asyncio.sleep(1.5)  # не спамим
            except FloodWaitError as e:
                logging.warning(f"⏳ Flood wait: ждём {e.seconds} сек.")
                await asyncio.sleep(e.seconds)
            except UserPrivacyRestrictedError:
                logging.warning(f"⛔ Приватность: не удалось написать {user_id}")
                fail_count += 1
            except Exception as e:
                logging.error(f"❌ Ошибка отправки {user_id}: {e}")
                fail_count += 1

        logging.info(f"Рассылка завершена. Успешно: {success_count}, Неудачно: {fail_count}")
        await client.disconnect()

    except Exception as e:
        logging.error(f"❌ Общая ошибка в run_sender: {e}")







