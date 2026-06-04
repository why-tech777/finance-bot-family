from aiogram import Router, F
from aiogram.types import Message
from config import ALLOWED_USERS
from database import get_history

router = Router()

ICONS = {"income": "➕", "expense": "➖"}


@router.message(F.text == "📜 История")
async def cmd_history(message: Message):
    if message.from_user.id not in ALLOWED_USERS:
        return

    rows = await get_history(limit=30)
    if not rows:
        await message.answer("📭 Операций пока нет")
        return

    lines = ["<b>📜 Последние операции:</b>\n"]
    for user_name, op_type, source, category, amount, comment, created_at in rows:
        date = created_at[:10]
        icon = ICONS.get(op_type, "•")
        cat  = f" [{category}]" if category else ""
        cmt  = f" — {comment}" if comment else ""
        sign = "+" if op_type == "income" else "-"
        lines.append(
            f"{icon} {date}  <b>{sign}{amount:,.2f} ₽</b>  {source}{cat}\n"
            f"   👤 {user_name}{cmt}"
        )

    await message.answer("\n".join(lines), parse_mode="HTML")
