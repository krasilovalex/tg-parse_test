from bd.bd_operations import BaseData
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from utils.utils import load_group_links, autorization_tg
from parsers.parsers_open import parse_open_subs
from parsers.parsers_closed import parse_subs_closed, get_linked_chat
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
    group_links = load_group_links() ## загрузка групп из .txt


    # обработка каждый ссылки по отдельности!!!
    for link in group_links:
        ready_chat = get_linked_chat(link, client)
        if ready_chat:
            parse_subs_closed(client, ready_chat, bd)
        else:
            parse_open_subs(client,link,bd)
            continue
    
    
    bd.close_connection_into_bd()
    client.disconnect()
    logging.info('Готово!')

if __name__ == '__main__':
    main()