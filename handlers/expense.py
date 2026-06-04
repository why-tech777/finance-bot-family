from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config import ALLOWED_USERS
from database import add_transaction
from keyboards.menu import menu
from keyboards.categories import sources_kb, categories_kb, VALID_SOURCES, VALID_CATEGORIES
from datetime import datetime
import pytz

router = Router()
tz = pytz.timezone("Europe/Moscow")


class ExpenseStates(StatesGroup):
    source   = State()
    amount   = State()
    category = State()
    comment  = State()


@router.message(F.text == "➖ Расход")
async def expense_start(message: Message, state: FSMContext):
    if message.from_user.id not in ALLOWED_USERS:
        return
    await state.set_state(ExpenseStates.source)
    await message.answer("💳 Источник оплаты:", reply_markup=sources_kb)


@router.message(ExpenseStates.source)
async def expense_source(message: Message, state: FSMContext):
    if message.text not in VALID_SOURCES:
        await message.answer("Пожалуйста, выбери из кнопок: Карта или Наличные", reply_markup=sources_kb)
        return
    await state.update_data(source=message.text)
    await state.set_state(ExpenseStates.amount)
    await message.answer("💰 Введи сумму (например: 1500):")


@router.message(ExpenseStates.amount)
async def expense_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", ".").replace(" ", ""))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Некорректная сумма. Введи число, например: 1500")
        return
    await state.update_data(amount=amount)
    await state.set_state(ExpenseStates.category)
    await message.answer("🗂 Выбери категорию:", reply_markup=categories_kb)


@router.message(ExpenseStates.category)
async def expense_category(message: Message, state: FSMContext):
    if message.text not in VALID_CATEGORIES:
        await message.answer("Пожалуйста, выбери категорию из кнопок", reply_markup=categories_kb)
        return
    await state.update_data(category=message.text)
    await state.set_state(ExpenseStates.comment)
    await message.answer("📝 Комментарий (или отправь — чтобы пропустить):")


@router.message(ExpenseStates.comment)
async def expense_comment(message: Message, state: FSMContext):
    data    = await state.get_data()
    uid     = message.from_user.id
    name    = ALLOWED_USERS[uid]
    comment = message.text if message.text != "—" else ""
    now     = datetime.now(tz).isoformat()

    await add_transaction(uid, name, "expense", data["source"], data["amount"], data["category"], comment, now)

    await message.answer(
        f"✅ Расход записан!\n"
        f"Сумма: {data['amount']:,.2f} ₽  |  {data['source']}\n"
        f"Категория: {data['category']}\n"
        f"Комментарий: {comment or '—'}",
        reply_markup=menu,
    )
    await state.clear()
