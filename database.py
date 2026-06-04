import aiosqlite
from config import DB_NAME

notify_callback = None


def set_notify_callback(func):
    global notify_callback
    notify_callback = func


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL,
                user_name      TEXT    NOT NULL,
                operation_type TEXT    NOT NULL,
                source         TEXT    NOT NULL,
                category       TEXT,
                amount         REAL    NOT NULL,
                comment        TEXT,
                created_at     TEXT    NOT NULL
            )
        """)
        await db.commit()


async def add_transaction(user_id, user_name, op_type, source, amount, category, comment, created_at):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """INSERT INTO transactions
               (user_id, user_name, operation_type, source, category, amount, comment, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, user_name, op_type, source, category, amount, comment, created_at),
        )
        await db.commit()

    if notify_callback:
        import asyncio
        asyncio.create_task(
            notify_callback(user_id, op_type, amount, category, comment, source)
        )


async def get_balance():
    """Returns (total_balance, card_balance, cash_balance)."""
    async with aiosqlite.connect(DB_NAME) as db:
        async def _sum(op_type, source=None):
            if source:
                cur = await db.execute(
                    "SELECT COALESCE(SUM(amount),0) FROM transactions "
                    "WHERE operation_type=? AND source=?",
                    (op_type, source),
                )
            else:
                cur = await db.execute(
                    "SELECT COALESCE(SUM(amount),0) FROM transactions WHERE operation_type=?",
                    (op_type,),
                )
            return (await cur.fetchone())[0]

        total_inc  = await _sum("income")
        total_exp  = await _sum("expense")
        card_inc   = await _sum("income",  "Карта")
        card_exp   = await _sum("expense", "Карта")
        cash_inc   = await _sum("income",  "Наличные")
        cash_exp   = await _sum("expense", "Наличные")

    return (
        total_inc - total_exp,
        card_inc  - card_exp,
        cash_inc  - cash_exp,
    )


async def get_history(limit=30):
    """Last `limit` transactions for both users."""
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            """SELECT user_name, operation_type, source, category, amount, comment, created_at
               FROM transactions
               ORDER BY id DESC
               LIMIT ?""",
            (limit,),
        )
        rows = await cur.fetchall()
    return rows


async def get_monthly_report(year: int, month: int):
    """
    Returns a dict with:
      income_total, expense_total,
      card_income, card_expense,
      cash_income, cash_expense,
      categories: {name: amount}
    """
    prefix = f"{year:04d}-{month:02d}"

    async with aiosqlite.connect(DB_NAME) as db:
        async def _sum(op_type, source=None):
            if source:
                cur = await db.execute(
                    "SELECT COALESCE(SUM(amount),0) FROM transactions "
                    "WHERE operation_type=? AND source=? AND created_at LIKE ?",
                    (op_type, source, prefix + "%"),
                )
            else:
                cur = await db.execute(
                    "SELECT COALESCE(SUM(amount),0) FROM transactions "
                    "WHERE operation_type=? AND created_at LIKE ?",
                    (op_type, prefix + "%"),
                )
            return (await cur.fetchone())[0]

        income_total  = await _sum("income")
        expense_total = await _sum("expense")
        card_income   = await _sum("income",  "Карта")
        card_expense  = await _sum("expense", "Карта")
        cash_income   = await _sum("income",  "Наличные")
        cash_expense  = await _sum("expense", "Наличные")

        cur = await db.execute(
            """SELECT category, COALESCE(SUM(amount),0)
               FROM transactions
               WHERE operation_type='expense' AND created_at LIKE ?
               GROUP BY category""",
            (prefix + "%",),
        )
        cat_rows = await cur.fetchall()

    categories = {row[0] or "Без категории": row[1] for row in cat_rows}

    return {
        "income_total":  income_total,
        "expense_total": expense_total,
        "card_income":   card_income,
        "card_expense":  card_expense,
        "cash_income":   cash_income,
        "cash_expense":  cash_expense,
        "categories":    categories,
    }


async def get_today_transactions(date_prefix: str):
    """All transactions for a given day (date_prefix = 'YYYY-MM-DD')."""
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            """SELECT user_name, operation_type, source, category, amount, comment
               FROM transactions
               WHERE created_at LIKE ?
               ORDER BY id""",
            (date_prefix + "%",),
        )
        rows = await cur.fetchall()
    return rows
