import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, ALLOWED_USERS
from database import init_db, set_notify_callback

from handlers.start import router as start_router
from handlers.income import router as income_router
from handlers.expense import router as expense_router
from handlers.history import router as history_router
from handlers.reports import router as reports_router
from handlers.transfer import router as transfer_router

from scheduler import setup


# -------------------------
# SAFETY CHECK (ВАЖНО)
# -------------------------
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Check Railway Variables!")


# -------------------------
# BOT INIT (правильный aiogram 3)
# -------------------------
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)

dp = Dispatcher()


# -------------------------
# ROUTERS
# -------------------------
dp.include_router(start_router)
dp.include_router(income_router)
dp.include_router(expense_router)
dp.include_router(history_router)
dp.include_router(reports_router)
dp.include_router(transfer_router)


# -------------------------
# NOTIFICATIONS
# -------------------------
async def notify_partner(uid, op_type, amount, category, comment, source):
    sender_name = ALLOWED_USERS.get(uid, f"ID {uid}")
    icon = "➕" if op_type == "income" else "➖"
    op_text = "пополнение" if op_type == "income" else "расход"

    cat = f" [{category}]" if category else ""
    cmt = f"\nКомментарий: {comment}" if comment else ""

    text = (
        f"{icon} <b>{sender_name}</b> записал {op_text}:\n"
        f"{amount:,.2f} ₽  |  {source}{cat}{cmt}"
    )

    for partner_id in ALLOWED_USERS:
        if partner_id != uid:
            try:
                await bot.send_message(partner_id, text)
            except Exception:
                pass


# -------------------------
# MAIN
# -------------------------
async def main():
    os.makedirs("/data", exist_ok=True)

    await init_db()
    set_notify_callback(notify_partner)

    setup(bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
