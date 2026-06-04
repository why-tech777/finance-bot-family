from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import ALLOWED_USERS, DAILY_REPORT_HOUR
from database import get_today_transactions
from datetime import datetime
import pytz

tz = pytz.timezone("Europe/Moscow")


def setup(bot):
    scheduler = AsyncIOScheduler(timezone=tz)

    async def daily_summary():
        today = datetime.now(tz).strftime("%Y-%m-%d")
        rows  = await get_today_transactions(today)

        if not rows:
            text = f"📅 <b>Сводка за {today}</b>\n\nСегодня операций не было."
        else:
            income_total  = sum(r[4] for r in rows if r[1] == "income")
            expense_total = sum(r[4] for r in rows if r[1] == "expense")
            lines = [f"📅 <b>Сводка за {today}</b>\n"]

            if income_total:
                lines.append(f"➕ Пополнения: <b>{income_total:,.2f} ₽</b>")
            if expense_total:
                lines.append(f"➖ Расходы:    <b>{expense_total:,.2f} ₽</b>")
            lines.append(f"💰 Итог дня:   <b>{income_total - expense_total:,.2f} ₽</b>\n")
            transfer_in = sum(r[4] for r in rows if r[1] == "transfer_in")
            transfer_out = sum(r[4] for r in rows if r[1] == "transfer_out")

            if transfer_in or transfer_out:
                lines.append(f"🔄 Переводы: <b>{max(transfer_in, transfer_out):,.2f} ₽</b>")

            lines.append("<b>Детали:</b>")

            for user_name, op_type, source, category, amount, comment in rows:
                if op_type == "income":
                    icon = "➕"
                elif op_type == "expense":
                    icon = "➖"
                elif op_type == "transfer_in":
                    icon = "⬅️"
                elif op_type == "transfer_out":
                    icon = "➡️"
                else:
                    icon = "🔄"
                cat  = f" [{category}]" if category else ""
                cmt  = f" — {comment}" if comment else ""
                lines.append(f"  {icon} {user_name}: {amount:,.2f} ₽  {source}{cat}{cmt}")

            text = "\n".join(lines)

        for uid in ALLOWED_USERS:
            try:
                await bot.send_message(uid, text, parse_mode="HTML")
            except Exception:
                pass

    scheduler.add_job(daily_summary, "cron", hour=DAILY_REPORT_HOUR, minute=0)
    scheduler.start()
    return scheduler
