from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config import ALLOWED_USERS
from database import add_transaction
from keyboards.menu import menu
from keyboards.categories import sources_kb, VALID_SOURCES
from datetime import datetime
import pytz

router = Router()
tz = pytz.timezone("Europe/Moscow")


class IncomeStates(StatesGroup):
    source  = State()
    amount  = State()
    comment = State()


@router.message(F.text == "➕ Пополнить")
async def income_start(message: Message, state: FSMContext):
    if message.from_user.id not in ALLOWED_USERS:
        return
    await state.set_state(IncomeStates.source)
    await message.answer("💳 Источник пополнения:", reply_markup=sources_kb)


@router.message(IncomeStates.source)
async def income_source(message: Message, state: FSMContext):
    if message.text not in VALID_SOURCES:
        await message.answer("Пожалуйста, выбери из кнопок: Карта или Наличные", reply_markup=sources_kb)
        return
    await state.update_data(source=message.text)
    await state.set_state(IncomeStates.amount)
    await message.answer("💰 Введи сумму (например: 5000):")


@router.message(IncomeStates.amount)
async def income_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", ".").replace(" ", ""))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Некорректная сумма. Введи число, например: 5000")
        return
    await state.update_data(amount=amount)
    await state.set_state(IncomeStates.comment)
    await message.answer("📝 Комментарий (или отправь — чтобы пропустить):")


@router.message(IncomeStates.comment)
async def income_comment(message: Message, state: FSMContext):
    data    = await state.get_data()
    uid     = message.from_user.id
    name    = ALLOWED_USERS[uid]
    comment = message.text if message.text != "—" else ""
    now     = datetime.now(tz).isoformat()

    await add_transaction(uid, name, "income", data["source"], data["amount"], None, comment, now)

    await message.answer(
        f"✅ Пополнение записано!\n"
        f"Сумма: {data['amount']:,.2f} ₽  |  {data['source']}\n"
        f"Комментарий: {comment or '—'}",
        reply_markup=menu,
    )
    await state.clear()
