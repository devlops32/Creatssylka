from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import os
import uuid
from datetime import datetime, timedelta
from config import PHOTO_FOLDER, BASE_URL, LINK_LIFETIME
from web_server import links

router = Router()

class PhotoState(StatesGroup):
    waiting_photo = State()

@router.message(F.text == "/start")
async def start_cmd(message: Message):
    kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="➕ Создать ссылку")]],
        resize_keyboard=True
    )
    await message.answer(
        "Привет, я создаю временные ссылки на фото!",
        reply_markup=kb
    )

@router.message(F.text == "➕ Создать ссылку")
async def create_link_start(message: Message, state: FSMContext):
    await state.set_state(PhotoState.waiting_photo)
    await message.answer("Отправьте фото", reply_markup=types.ReplyKeyboardRemove())

@router.message(PhotoState.waiting_photo, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_path = file.file_path
    
    os.makedirs(PHOTO_FOLDER, exist_ok=True)
    unique_id = str(uuid.uuid4())[:8]
    local_path = os.path.join(PHOTO_FOLDER, f"{unique_id}.jpg")
    
    await message.bot.download_file(file_path, local_path)
    
    # Отправляем "создаю ссылку"
    loading_msg = await message.answer("🕒 Создаю ссылку...")
    
    # Генерируем ссылку
    link_id = unique_id
    expire_time = datetime.now() + timedelta(seconds=LINK_LIFETIME)
    links[link_id] = (local_path, expire_time)
    full_url = f"{BASE_URL}/photo/{link_id}"
    
    # Ждём 5 секунд
    await asyncio.sleep(5)
    await loading_msg.delete()
    
    # Отправляем ссылку инлайн-кнопкой
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Ссылка на страницу", url=full_url)]]
    )
    await message.answer("Ваша ссылка", reply_markup=kb)
    await state.clear()

# Заглушка для asyncio в этом файле
import asyncio