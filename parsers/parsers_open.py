from bd.bd_operations import BaseData
import logging


def parse_open_subs(group_link, client, bd):
    """
    Парсит участников открытой группы.
    Добавляет их в базу данных.
    """
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
