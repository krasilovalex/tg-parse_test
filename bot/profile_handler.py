from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, FSInputFile
from aiogram import Router, F
from aiogram.enums.parse_mode import ParseMode
from utils.load_auth_data import load_auth_data
from pathlib import Path
from aiogram.fsm.context import FSMContext


from bot.handlers_parse import start_parse
from bot.handlers_sender import start_sender

BD_PATH = Path("users.db").resolve()


def get_profile_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text = "🔍 Парсить", callback_data="do_parse"),
            InlineKeyboardButton(text = "📤 Рассылка", callback_data = "do_sender"),
            InlineKeyboardButton(text="⚠️ Очистить базу данных", callback_data = "clear_db")
        ]
    ])


profile_router = Router()


@profile_router.message(F.text == "/profile")
async def cmd_profile(message: Message):
    user_id = str(message.from_user.id)
    data = load_auth_data()

    if user_id not in data:
        await message.answer("⚠️ Вы еще не авторизовались. Используйте /start")
        return
    
    user = data[user_id]
    profile_text = (
        f"<b>Личный кабинет:</b>\n\n"
        f"<b>🆔 API_ID:</b> <code>{user['api_id']}</code>\n"
        f"<b>🔑 API_HASH:</b> <code>{user['api_hash']}</code>\n"
    )
    await message.answer(profile_text, parse_mode=ParseMode.HTML, reply_markup=get_profile_keyboard())


@profile_router.callback_query(F.data == "do_parse")
async def profile_do_parse_handler(callback: CallbackQuery):
    # Имитация объекта message для передачи в start_parse
    class DummyMessage:
        def __init__(self, from_user, chat):
            self.from_user = from_user
            self.chat = chat
        async def answer(self, *args, **kwargs):
            await callback.message.answer(*args, **kwargs)

    dummy_message = DummyMessage(callback.from_user, callback.message.chat)
    await start_parse(dummy_message)
    await callback.answer()

@profile_router.callback_query(F.data == "do_sender")
async def profile_do_sender_handler(callback: CallbackQuery, state: FSMContext):
    # Имитация объекта message для передачи в start_parse
    class DummyMessage:
        def __init__(self, from_user, chat):
            self.from_user = from_user
            self.chat = chat
        async def answer(self, *args, **kwargs):
            await callback.message.answer(*args, **kwargs)

    dummy_message = DummyMessage(callback.from_user, callback.message.chat)
    await start_sender(dummy_message, state)
    await callback.answer()


@profile_router.callback_query(F.data == "clear_db")
async def clear_db_query(callback: CallbackQuery):
    file = FSInputFile(path=BD_PATH, filename="users.db")
    with open(BD_PATH, 'w', encoding="utf-8") as f:
                        f.truncate(0)
    await callback.message.answer("База данных успешно очищена")
