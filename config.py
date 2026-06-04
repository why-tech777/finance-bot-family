import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ALLOWED_USERS = {
    414499892: "Дмитрий",
    8764803039: "Ксения",
}

DB_NAME = os.getenv("DB_PATH", "/data/finance.db")
TIMEZONE = "Europe/Moscow"
DAILY_REPORT_HOUR = 22
