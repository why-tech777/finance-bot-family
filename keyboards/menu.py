from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Баланс")],
        [KeyboardButton(text="➕ Пополнить")],
        [KeyboardButton(text="➖ Расход")],
        [KeyboardButton(text="🔄 Перевод")],
        [KeyboardButton(text="📜 История")],
        [KeyboardButton(text="📊 Отчёт")],
    ],
    resize_keyboard=True,
)
