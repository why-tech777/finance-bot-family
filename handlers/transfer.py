
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime
import pytz
from config import ALLOWED_USERS
from database import add_transaction
from keyboards.menu import menu

router = Router()
tz = pytz.timezone("Europe/Moscow")

transfer_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="💳 → 💵")],
    [KeyboardButton(text="💵 → 💳")],
    [KeyboardButton(text="⬅️ Назад")]
], resize_keyboard=True)

back_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="⬅️ Назад")]
], resize_keyboard=True)

class TransferStates(StatesGroup):
    direction = State()
    amount = State()

@router.message(F.text == "🔄 Перевод")
async def start_transfer(message: Message, state: FSMContext):
    await state.set_state(TransferStates.direction)
    await message.answer("Выберите направление перевода:", reply_markup=transfer_kb)

@router.message(F.text == "⬅️ Назад")
async def back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=menu)

@router.message(TransferStates.direction)
async def direction(message: Message, state: FSMContext):
    if message.text not in ("💳 → 💵", "💵 → 💳"):
        return
    await state.update_data(direction=message.text)
    await state.set_state(TransferStates.amount)
    await message.answer("Введите сумму:", reply_markup=back_kb)

@router.message(TransferStates.amount)
async def amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except:
        await message.answer("Введите корректную сумму.")
        return

    data = await state.get_data()

    if data["direction"] == "💳 → 💵":
        from_source = "Карта"
        to_source = "Наличные"
    else:
        from_source = "Наличные"
        to_source = "Карта"

    now = datetime.now(tz).isoformat()
    uid = message.from_user.id
    uname = ALLOWED_USERS[uid]

    await add_transaction(uid, uname, "transfer_out", from_source, amount, "Перевод", "Перевод", now)
    await add_transaction(uid, uname, "transfer_in", to_source, amount, "Перевод", "Перевод", now)

    await state.clear()
    await message.answer("✅ Перевод выполнен", reply_markup=menu)
