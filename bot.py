import asyncio
import os
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, ALLOWED_USERS
from database import init_db, set_notify_callback

from handlers.start   import router as start_router
from handlers.income  import router as income_router
from handlers.expense import router as expense_router
from handlers.history import router as history_router
from handlers.reports import router as reports_router

from scheduler import setup

bot = Bot(BOT_TOKEN)
dp  = Dispatcher()

dp.include_router(start_router)
dp.include_router(income_router)
dp.include_router(expense_router)
dp.include_router(history_router)
dp.include_router(reports_router)


async def notify_partner(uid, op_type, amount, category, comment, source):
    """Send a notification to the *other* user when a transaction is added."""
    sender_name = ALLOWED_USERS.get(uid, f"ID {uid}")
    icon = "➕" if op_type == "income" else "➖"
    op_text = "пополнение" if op_type == "income" else "расход"
    cat  = f" [{category}]" if category else ""
    cmt  = f"\nКомментарий: {comment}" if comment else ""

    text = (
        f"{icon} <b>{sender_name}</b> записал {op_text}:\n"
        f"{amount:,.2f} ₽  |  {source}{cat}{cmt}"
    )

    for partner_id in ALLOWED_USERS:
        if partner_id != uid:
            try:
                await bot.send_message(partner_id, text, parse_mode="HTML")
            except Exception:
                pass


async def main():
    # Ensure /data directory exists (Railway persistent volume)
    os.makedirs("/data", exist_ok=True)

    await init_db()
    set_notify_callback(notify_partner)
    setup(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
