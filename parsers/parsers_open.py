from bd.bd_operations import BaseData
import logging


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
        try:
            bd.add_in_db(user_id)
            logging.info(f"Добавлен в БД: {user.username} ({user_id})")
        except Exception as e:
            logging.error(f"Ошибка при добавлении пользователя {user_id}")
