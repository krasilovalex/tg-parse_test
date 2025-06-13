from utils.utils import authorize
from parsers.parsers_open import parse_open_subs
from parsers.parsers_closed import parse_subs_closed, get_linked_chat
from services.bd_operations import BaseData
from utils.utils import load_group_links
from services.sender import send_invites
from core.update_envs import get_account_data
import logging
from dotenv import load_dotenv
import time

load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    handlers=[
        logging.FileHandler('parse_test_log.txt'),
        logging.StreamHandler()
    ]
)

def main() :
    """
    Основная функция запуска парсинга и рассылки. Группы хранятся в groups.txt
    """
    logging.info("Запуска скрипта")
    bd = BaseData()
    bd.create_bd_if_not_exists()
    
    client_data = get_account_data(prefix='PARSER', default_session='pars_account')
    parser_client = authorize(client_data)
    logging.info(f"Авторизован как парсер: {parser_client.get_me().username}")
    group_links = load_group_links()

    for link in group_links:
        ready_chat = get_linked_chat(link, parser_client)
        if ready_chat:
            parse_subs_closed(parser_client, ready_chat, bd)
        else:
            parse_open_subs(parser_client, link, bd)
            continue
    parser_client.disconnect()
    time.sleep(20)
    sender_data = get_account_data(prefix='SENDER', default_session='send_account')
    sender_client = authorize(sender_data)
    logging.info(f"Авторизован как отправитель: {sender_client.get_me().username}")
    send_invites(sender_client, bd, delay=10)

    sender_client.disconnect()

    bd.close_connection_into_bd
    logging.info(f"Бд закрыло соединение")


if __name__ == '__main__':
    main()
