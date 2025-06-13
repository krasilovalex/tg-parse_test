#  tg-parse_test

**tg-parse_test** — это инструмент на Python для сбора подписчиков (открытых участников и комментаторов закрытых каналов) из Telegram-групп/каналов и рассылки им приглашений в новый чат или клуб. Он состоит из двух частей: `parser` (сбор пользователей) и `sender` (рассылка сообщений), каждый из которых запускается отдельно.

---

##  Возможности

- Собирает участников открытых групп
- Собирает активных комментаторов из обсуждений закрытых каналов
- Сохраняет `user_id`, `username` и `access_hash` каждого пользователя в SQLite
- Делает рассылку сообщений с задержкой между отправками

---




# Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/krasilovalex/tg-parse_test.git
   cd tg-parse_test
Установите зависимости:
pip install -r requirements.txt

Настройте .env (пример ниже).
Создайте файл .env и добавьте следующие переменные:
# Парсер (сбор участников)
PARSER_SESSION=pars_account

PARSER_PHONE_NUMBER=+7...

PARSER_PASSWORD=...

PARSER_API_ID=123456

PARSER_API_HASH=xxxx

PARSER_SYSTEM_VERSION=...

PARSER_DEVICE_MODEL=...


# Отправитель (рассылка)
SENDER_SESSION=send_account

SENDER_PHONE_NUMBER=+7...

SENDER_PASSWORD=...

SENDER_API_ID=654321

SENDER_API_HASH=yyyy

SENDER_SYSTEM_VERSION=...

SENDER_DEVICE_MODEL=...



# Структура проекта
.
├── load_pars.py          # Запуск сбора пользователей

├── load_send.py          # Запуск рассылки сообщений

├── parsers/
│   ├── parsers_open.py   # Сбор участников из открытых групп

│   └── parsers_closed.py # Сбор комментаторов из обсуждений

├── sendmsg/
│   └── send_message.py   # Модуль рассылки приглашений

├── utils/
│   └── utils.py          # Вспомогательные функции

├── bd/
│   └── bd_operations.py  # Класс работы с SQLite БД

└── requirements.txt



# Как использовать
Парсинг (load_pars.py)

Этот скрипт подключается под Telegram-аккаунтом для сбора пользователей, сохраняет их в users.db.
   ```
   python load_pars.py
   ```
Рассылка (load_send.py)
Этот скрипт подключается другим Telegram-аккаунтом, читает пользователей из БД и отправляет им тексты приглашений.
```
python load_send.py
