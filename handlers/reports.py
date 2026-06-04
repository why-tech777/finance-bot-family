from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config import ALLOWED_USERS
from database import get_monthly_report
from keyboards.menu import menu
from datetime import datetime
import pytz
import io

router = Router()
tz = pytz.timezone("Europe/Moscow")

MONTH_NAMES = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь",
}


class ReportStates(StatesGroup):
    month = State()


@router.message(F.text == "📊 Отчёт")
async def report_start(message: Message, state: FSMContext):
    if message.from_user.id not in ALLOWED_USERS:
        return
    now = datetime.now(tz)
    await state.set_state(ReportStates.month)
    await message.answer(
        f"📅 За какой месяц показать отчёт?\n"
        f"Введи в формате <b>ММ.ГГГГ</b> (например <code>{now.month:02d}.{now.year}</code>):",
        parse_mode="HTML",
    )


@router.message(ReportStates.month)
async def report_month(message: Message, state: FSMContext):
    await state.clear()
    try:
        month_str, year_str = message.text.strip().split(".")
        month = int(month_str)
        year  = int(year_str)
        if not (1 <= month <= 12):
            raise ValueError
    except ValueError:
        await message.answer("❌ Неверный формат. Пример: 06.2025", reply_markup=menu)
        return

    data = await get_monthly_report(year, month)
    month_name = MONTH_NAMES[month]

    text = (
        f"📊 <b>Отчёт за {month_name} {year}</b>\n\n"
        f"➕ Доходы:   <b>{data['income_total']:,.2f} ₽</b>\n"
        f"➖ Расходы:  <b>{data['expense_total']:,.2f} ₽</b>\n"
        f"💰 Итог:     <b>{data['income_total'] - data['expense_total']:,.2f} ₽</b>\n\n"
        f"<b>💳 Карта:</b>\n"
        f"   Доходы: {data['card_income']:,.2f} ₽\n"
        f"   Расходы: {data['card_expense']:,.2f} ₽\n"
        f"   Баланс: {data['card_income'] - data['card_expense']:,.2f} ₽\n\n"
        f"<b>💵 Наличные:</b>\n"
        f"   Доходы: {data['cash_income']:,.2f} ₽\n"
        f"   Расходы: {data['cash_expense']:,.2f} ₽\n"
        f"   Баланс: {data['cash_income'] - data['cash_expense']:,.2f} ₽\n"
    )

    if data["categories"]:
        text += "\n<b>🗂 Расходы по категориям:</b>\n"
        for cat, amt in sorted(data["categories"].items(), key=lambda x: -x[1]):
            text += f"   • {cat}: {amt:,.2f} ₽\n"

    await message.answer(text, parse_mode="HTML", reply_markup=menu)

    # Send pie chart if there are categories
    if data["categories"]:
        chart = _build_chart(data["categories"], month_name, year)
        if chart:
            await message.answer_photo(
                BufferedInputFile(chart, filename="report.png"),
                caption=f"📈 График расходов — {month_name} {year}",
            )


def _build_chart(categories: dict, month_name: str, year: int) -> bytes | None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        labels = list(categories.keys())
        values = list(categories.values())

        fig, ax = plt.subplots(figsize=(6, 5))
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            pctdistance=0.82,
        )
        for t in autotexts:
            t.set_fontsize(9)

        ax.set_title(f"Расходы по категориям\n{month_name} {year}", fontsize=13, pad=14)
        fig.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=130)
        plt.close(fig)
        buf.seek(0)
        return buf.read()
    except Exception:
        return None
