from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from core.client import get_telethon_client
from core.controller import run_sender
from services.bd_operations import BaseData
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
import os
import logging
from pathlib import Path
import asyncio
import traceback

sender_router = Router()

class SenderStates(StatesGroup):
    awaiting_api_id = State()
    awaiting_api_hash = State()
    awaiting_phone = State()
    awaiting_password = State()
    awaiting_system = State()
    awaiting_device = State()
    awaiting_code = State()
    awaiting_db_file = State()
    awaiting_message_text = State()

@sender_router.message(Command("sender"))
async def start_sender(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    logging.info(f"Команда /sender вызвана пользователем {user_id}")

    await state.clear()
    await state.set_state(SenderStates.awaiting_api_id)
    await message.answer("Введите ваш <b>api_id</b>:", parse_mode=ParseMode.HTML)

@sender_router.message(SenderStates.awaiting_api_id)
async def input_api_id(message: types.Message, state: FSMContext):
    try:
        api_id = int(message.text.strip())
    except (ValueError, AttributeError):
        await message.answer("❌ api_id должен быть числом. Попробуйте еще раз.")
        return
    await state.update_data(api_id=api_id)
    await state.set_state(SenderStates.awaiting_api_hash)
    await message.answer("Введите ваш <b>api_hash</b>:", parse_mode=ParseMode.HTML)

@sender_router.message(SenderStates.awaiting_api_hash)
async def input_api_hash(message: types.Message, state: FSMContext):
    api_hash = message.text.strip()
    await state.update_data(api_hash=api_hash)
    await state.set_state(SenderStates.awaiting_phone)
    await message.answer("Введите ваш <b>phone_number</b> в формате +7...:", parse_mode=ParseMode.HTML)

@sender_router.message(SenderStates.awaiting_phone)
async def input_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    await state.update_data(phone=phone)
    await state.set_state(SenderStates.awaiting_password)
    await message.answer("Введите <b>пароль</b> (если 2FA включена, иначе любой символ):", parse_mode=ParseMode.HTML)

@sender_router.message(SenderStates.awaiting_password)
async def input_password(message: types.Message, state: FSMContext):
    password = message.text.strip()
    await state.update_data(password=password)
    await state.set_state(SenderStates.awaiting_system)
    await message.answer("Введите <b>system_version</b> (например: Windows 11):", parse_mode=ParseMode.HTML)

@sender_router.message(SenderStates.awaiting_system)
async def input_system(message: types.Message, state: FSMContext):
    system = message.text.strip()
    await state.update_data(system=system)
    await state.set_state(SenderStates.awaiting_device)
    await message.answer("Введите <b>device_model</b> (например: PC Club):", parse_mode=ParseMode.HTML)

@sender_router.message(SenderStates.awaiting_device)
async def input_device(message: types.Message, state: FSMContext):
    device = message.text.strip()
    await state.update_data(device=device)

    data = await state.get_data()

    try:
        client, is_code_required = await get_telethon_client(
            data["api_id"],
            data["api_hash"],
            data["phone"],
            data["password"],
            device,
            data["system"],
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при подключении к Telethon: {e}")
        logging.error(f"Ошибка при get_telethon_client: {e}\n{traceback.format_exc()}")
        await state.clear()
        return

    if is_code_required:
        await state.update_data(client=client)
        await state.set_state(SenderStates.awaiting_code)
        await message.answer("📲 Введите код подтверждения из Telegram:")
    else:
        await state.update_data(client=client)
        await state.set_state(SenderStates.awaiting_db_file)
        await message.answer("📎 Пришлите файл базы данных <b>users.db</b>, полученный после /parse:", parse_mode=ParseMode.HTML)

@sender_router.message(SenderStates.awaiting_code)
async def input_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    data = await state.get_data()
    client = data.get("client")
    phone = data.get("phone")
    password = data.get("password")

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
    except Exception as e:
        await message.answer(f"❌ Ошибка авторизации: {e}")
        logging.error(f"Ошибка авторизации: {e}\n{traceback.format_exc()}")
        return

    await state.set_state(SenderStates.awaiting_db_file)
    await message.answer("✅ Авторизация успешна! Пришлите файл базы данных <b>users.db</b>:", parse_mode=ParseMode.HTML)

@sender_router.message(SenderStates.awaiting_db_file, F.document)
async def handle_sender_db(message: types.Message, state: FSMContext):
    file = message.document
    if not file.file_name.endswith(".db"):
        await message.answer("❌ Пожалуйста, отправьте корректный .db файл.")
        return

    user_id = message.from_user.id
    db_path = f"temp_users_{user_id}.db"

    try:
        # Используем загрузку через bot.download, если download у document нет
        await message.bot.download(file=file.file_id, destination=db_path)

        logging.info(f"User {user_id} загрузил файл базы {db_path}, size={os.path.getsize(db_path)}")
        await state.update_data(db_path=db_path)
        await state.set_state(SenderStates.awaiting_message_text)
        await message.answer("✉️ Теперь введите текст сообщения, которое хотите отправить.")
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла базы от user {user_id}: {e}")
        await message.answer(f"❌ Ошибка при загрузке файла: {e}")


@sender_router.message(SenderStates.awaiting_message_text)
async def input_message_text(message: types.Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()

    if not data.get("db_path"):
        await message.answer("❌ Ошибка: база данных не загружена.")
        return

    await state.update_data(message_text=text)

    bd = BaseData(data["db_path"])

    # Проверяем наличие всех нужных параметров для создания клиента
    required_params = ("api_id", "api_hash", "phone", "device", "system")
    if not all(param in data for param in required_params):
        await message.answer("❌ Ошибка: не все параметры для подключения к Telethon заданы.")
        return

    # Запускаем рассылку в фоне, передавая все параметры для клиента
    client = data.get("client")
    asyncio.create_task(run_sender(
        client=client,
        bd=bd,
        message_text=text
    ))

    await message.answer("✅ Рассылка запущена в фоне!")

    # Удаляем временную базу и очищаем данные
    try:
        os.remove(data["db_path"])
    except Exception as e:
        logging.error(f"Ошибка удаления файла базы {data['db_path']}: {e}")

    await state.clear()
