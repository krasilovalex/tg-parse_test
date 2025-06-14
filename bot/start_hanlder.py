from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from utils.load_auth_data import load_auth_data, save_auth_data
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, FSInputFile

from bot.profile_handler import cmd_profile
class AuthState(StatesGroup):
    api_id = State()
    api_hash = State()
    phone = State()
    password = State()

start_router = Router()

@start_router.message(F.text == "/start")
async def start_auth(message:Message, state: FSMContext):
    user_id = str(message.from_user.id)
    data = load_auth_data()

    if user_id in data:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅Перейти к ЛК", callback_data="cab")],
        ])
        await message.answer("✅ Вы уже авторизованы, используйте кнопку ниже для доступа к личному кабинету", reply_markup=keyboard)
    else:
        await message.answer("Введите ваш <b>API_ID</b>", parse_mode=ParseMode.HTML)
        await state.set_state(AuthState.api_id)


@start_router.message(AuthState.api_id)
async def input_api_id(message : Message, state : FSMContext):
    await state.update_data(api_id = int(message.text))
    await message.answer("Введите ваш <b> API_HASH </b>", parse_mode=ParseMode.HTML)
    await state.set_state(AuthState.api_hash)

@start_router.message(AuthState.api_hash)
async def input_api_hash(message : Message, state : FSMContext):
    await state.update_data(api_hash = message.text)
    await message.answer("Введите <b>phone_number</b> в формате +7...", parse_mode=ParseMode.HTML)
    await state.set_state(AuthState.phone)

@start_router.message(AuthState.phone)
async def input_phone(message: Message, state: FSMContext):
    await state.update_data(phone = message.text)
    await message.answer("Введите ваш <b>пароль</b> (Если 2FA включена, иначе любой символ)", parse_mode=ParseMode.HTML)
    await state.set_state(AuthState.password)

@start_router.message(AuthState.password)
async def input_password(message: Message, state : FSMContext):
    user_id = str(message.from_user.id)
    user_data = await state.get_data()
    user_data['password'] = message.text

    all_data = load_auth_data()
    all_data[user_id] = user_data
    save_auth_data(all_data)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅Перейти к ЛК", callback_data="cab")],
        ])
    await message.answer("✅ Данные сохранены. Теперь используйте кнопку ниже для доступа к ЛК", reply_markup=keyboard)
    await state.clear()


@start_router.callback_query(F.data == "cab")
async def profile_do_sender_handler(callback: CallbackQuery):
    # Имитация объекта message для передачи в start_parse
    class DummyMessage:
        def __init__(self, from_user, chat):
            self.from_user = from_user
            self.chat = chat
        async def answer(self, *args, **kwargs):
            await callback.message.answer(*args, **kwargs)

    dummy_message = DummyMessage(callback.from_user, callback.message.chat)
    await cmd_profile(dummy_message)
    await callback.answer()