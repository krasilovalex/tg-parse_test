import logging
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from core.update_envs import get_account_data

_client = None
phone_number = ''
clients_waiting_code = {}


async def get_telethon_client(
    api_id: int,
    api_hash: str,
    phone_number: str,
    session_name: str = 'session_user.session'
):
    global _client

    device_model = "Windows PC"
    system_version = "10.0"

    if _client is not None:
        if _client.is_connected:
            if await _client.is_user_authorized():
                return _client, False  # False - код не нужен
            else:
                return _client, True   # True - код нужен (AUTH_REQUIRED)
        else:
            _client = None

    _client = TelegramClient(
        session_name,
        api_id,
        api_hash,
        device_model=device_model,
        system_version=system_version
    )

    await _client.connect()

    if not await _client.is_user_authorized():
        await _client.send_code_request(phone_number)
        clients_waiting_code[phone_number] = _client
        return _client, True  # код нужен

    clients_waiting_code[phone_number] = _client
    return _client, False  # код не нужен
