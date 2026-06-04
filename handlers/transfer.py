from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from config import ALLOWED_USERS
from database import add_transaction
from keyboards.menu import menu

from datetime import datetime
import pytz

router = Router()
tz = pytz.timezone("Europe/Moscow")

transfer_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 → 💵")],
        [KeyboardButton(text="💵 → 💳")],
    ],
    resize_keyboard=True,
)

class TransferStates(StatesGroup):
    direction = State()
    amount = State()

@router.message(F.text == "🔄 Перевод")
async def transfer_start(message: Message, state: FSMContext):
    if message.from_user.id not in ALLOWED_USERS:
        return
    await state.set_state(TransferStates.direction)
    await message.answer("Выбери направление перевода:", reply_markup=transfer_kb)

@router.message(TransferStates.direction)
async def transfer_direction(message: Message, state: FSMContext):
    if message.text not in ("💳 → 💵", "💵 → 💳"):
        await message.answer("Выбери вариант кнопкой.")
        return

    await state.update_data(direction=message.text)
    await state.set_state(TransferStates.amount)
    await message.answer("Введите сумму перевода:")

@router.message(TransferStates.amount)
async def transfer_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", ".").replace(" ", ""))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите корректную сумму.")
        return

    data = await state.get_data()
    uid = message.from_user.id
    name = ALLOWED_USERS[uid]
    now = datetime.now(tz).isoformat()

    if data["direction"] == "💳 → 💵":
        from_source = "Карта"
        to_source = "Наличные"
    else:
        from_source = "Наличные"
        to_source = "Карта"

    await add_transaction(uid, name, "expense", from_source, amount, "Перевод", "Перевод между счетами", now)
    await add_transaction(uid, name, "income", to_source, amount, None, "Перевод между счетами", now)

    await message.answer(
        f"✅ Перевод выполнен\n\n{from_source} → {to_source}\nСумма: {amount:,.2f} ₽",
        reply_markup=menu
    )

    await state.clear()
