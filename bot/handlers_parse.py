from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from core.controller import run_parser 
from core.client import  get_telethon_client
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from aiogram.types import FSInputFile
import os
from pathlib import Path

parse_router = Router()
pending_auth = {}  # {user_id: {..., "awaiting_2fa_password": False}}
step_state = {}    # user_id: current_step
sender_auth = {} # sender авторизация
sender_step = {} # user_id: current_step

# Получаем абсолютный путь к файлу users.db
BD_PATH = Path("users.db").resolve()

@parse_router.message(Command("parse"))
async def start_parse(message: types.Message):
    user_id = message.from_user.id
    pending_auth[user_id] = {}
    step_state[user_id] = "awaiting_api_id"
    await message.answer("Введите ваш <b>api_id</b>:", parse_mode=ParseMode.HTML)

@parse_router.message(lambda m: step_state.get(m.from_user.id))
async def parse_flow(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_id not in step_state:
        return  # Не запрашивали /parse

    step = step_state[user_id]

    try:
        if step == "awaiting_api_id":
            pending_auth[user_id]["api_id"] = int(text)
            await message.answer("Введите ваш <b>api_hash</b>:", parse_mode=ParseMode.HTML)
            step_state[user_id] = "awaiting_api_hash"

        elif step == "awaiting_api_hash":
            pending_auth[user_id]["api_hash"] = text
            await message.answer("Введите ваш <b>phone_number</b> в формате +7...:", parse_mode=ParseMode.HTML)
            step_state[user_id] = "awaiting_phone"

        elif step == "awaiting_phone":
            pending_auth[user_id]["phone"] = text
            await message.answer("Введите <b>пароль</b> (если 2FA включена, иначе любой символ):", parse_mode=ParseMode.HTML)
            step_state[user_id] = "awaiting_password"

        elif step == "awaiting_password":
            pending_auth[user_id]["password"] = text
            await message.answer("Введите <b>system_version</b> (например: Windows 11):", parse_mode=ParseMode.HTML)
            step_state[user_id] = "awaiting_system"

        elif step == "awaiting_system":
            pending_auth[user_id]["system"] = text
            await message.answer("Введите <b>device_model</b> (например: PC Club):", parse_mode=ParseMode.HTML)
            step_state[user_id] = "awaiting_device"

        elif step == "awaiting_device":
            pending_auth[user_id]["device"] = text
            await message.answer("Введите ссылки на группы через запятую:", parse_mode=ParseMode.HTML)
            step_state[user_id] = "awaiting_links"

        elif step == "awaiting_links":
            pending_auth[user_id]["group_links"] = text
            await message.answer("🔄 Начинаю авторизацию и парсинг...")

            data = pending_auth[user_id]
            client, is_code_required = await get_telethon_client(
                data["api_id"],
                data["api_hash"],
                data["phone"],
                data["password"],
                data["device"],
                data["system"]
            )

            if is_code_required:
                await message.answer("📲 Введите код подтверждения из Telegram:")
                step_state[user_id] = "awaiting_code"
                pending_auth[user_id]["client"] = client
                return

            await finish_parsing_flow(message, data, client)

            del pending_auth[user_id]
            del step_state[user_id]

        elif step == "awaiting_code":
            client = pending_auth[user_id]["client"]
            phone = pending_auth[user_id]["phone"]
            password = pending_auth[user_id]["password"]
            code = text

            try:
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                try:
                    await client.sign_in(password=password)
                except Exception as e:
                    await message.answer(f"❌ Ошибка при вводе пароля 2FA: {e}")
                    return
            except PhoneCodeInvalidError:
                await message.answer("❌ Неверный код. Попробуйте снова.")
                return

            await message.answer("✅ Авторизация успешна. Запускаю парсер...")

            data = pending_auth[user_id]
            await finish_parsing_flow(message, data, client)

            del pending_auth[user_id]
            del step_state[user_id]

    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {e}")


async def finish_parsing_flow(message, data, client):
    try:
        group_links = [link.strip() for link in data["group_links"].split(",") if link.strip()]
        results = await run_parser(group_links, client)

        # Отправка результатов парсинга
        msg = "✅ Парсинг завершён:\n"
        for group, count in results.items():
            msg += f"{group}: {count}\n"
        await message.answer(msg)

        # Проверка и отправка базы данных
        if os.path.exists(BD_PATH):
            file_size = os.path.getsize(BD_PATH)
            if file_size > 0:
                try:
                    file = FSInputFile(path=BD_PATH, filename="users.db")
                    await message.answer(f"✅ Найдена БД по пути: {BD_PATH}")
                    await message.answer_document(FSInputFile(BD_PATH), caption="📦 Вот ваша база данных users.db для /sender")
                    
                    # Очистка файла после успешной отправки
                    with open(BD_PATH, 'w', encoding="utf-8") as f:
                        f.truncate(0)
                except Exception as send_err:
                    await message.answer(f"❌ Не удалось отправить файл users.db: {send_err}")
            else:
                await message.answer("⚠️ Файл users.db пуст, нечего отправлять.")
        else:
            await message.answer(f"❌ Файл users.db не найден.\n\nПуть: {BD_PATH}")
    
    except Exception as e:
        await message.answer(f"❌ Ошибка во время парсинга или отправки файла: {e}")
