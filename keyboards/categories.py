from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

sources_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Карта"), KeyboardButton(text="Наличные")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

categories_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Еда"),        KeyboardButton(text="Транспорт")],
        [KeyboardButton(text="Квартира"),   KeyboardButton(text="Подписки")],
        [KeyboardButton(text="Другое")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

VALID_SOURCES    = {"Карта", "Наличные"}
VALID_CATEGORIES = {"Еда", "Транспорт", "Квартира", "Подписки", "Другое"}
