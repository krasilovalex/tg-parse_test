from core.config_env import Config

def get_account_data(prefix: str, default_session: str) -> dict:
    config_data = Config()

    api_id_str = config_data.get_env(f'{prefix}_API_ID')
    if api_id_str is None:
        raise ValueError(f"Переменная окружения {prefix}_API_ID не найдена")

    api_hash = config_data.get_env(f'{prefix}_API_HASH')
    if api_hash is None:
        raise ValueError(f"Переменная окружения {prefix}_API_HASH не найдена")

    phone_number = config_data.get_env(f'{prefix}_PHONE_NUMBER')
    if phone_number is None:
        raise ValueError(f"Переменная окружения {prefix}_PHONE_NUMBER не найдена")

    # Остальные поля могут быть необязательными, но можно тоже проверить если надо
    password = config_data.get_env(f'{prefix}_PASSWORD')  # пароль может быть None
    system_version = config_data.get_env(f'{prefix}_SYSTEM_VERSION') or 'Unknown'
    device_model = config_data.get_env(f'{prefix}_DEVICE_MODEL') or 'Unknown'

    return {
        'session_name': default_session,
        'api_id': int(api_id_str),
        'api_hash': api_hash,
        'phone_number': phone_number,
        'password': password,
        'system_version': system_version,
        'device_model': device_model
    }

