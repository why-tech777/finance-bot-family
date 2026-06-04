from aiogram import Router, F
from aiogram.types import Message
from config import ALLOWED_USERS
from database import get_balance
from keyboards.menu import menu

router = Router()


def _access(message: Message) -> bool:
    return message.from_user.id in ALLOWED_USERS


@router.message(F.text == "/start")
async def cmd_start(message: Message):
    if not _access(message):
        await message.answer("⛔ Доступ запрещён")
        return
    name = ALLOWED_USERS[message.from_user.id]
    await message.answer(f"Привет, {name}! 👋\nВыбери действие:", reply_markup=menu)


@router.message(F.text == "💰 Баланс")
async def cmd_balance(message: Message):
    if not _access(message):
        return
    total, card, cash = await get_balance()
    await message.answer(
        f"💰 <b>Общий баланс:</b> {total:,.2f} ₽\n"
        f"💳 Карта: {card:,.2f} ₽\n"
        f"💵 Наличные: {cash:,.2f} ₽",
        parse_mode="HTML",
    )
