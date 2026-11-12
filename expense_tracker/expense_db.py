import csv
import math
import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "expenses.db")

DEFAULT_CATEGORIES = [
    "Food", "Transport", "Shopping", "Bills",
    "Entertainment", "Health", "Education", "Other",
]


def parse_date(text):
    try:
        return datetime.strptime(str(text).strip(), "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise ValueError("Date must be a real date in YYYY-MM-DD format.")


def parse_amount(text):
    try:
        value = float(str(text).strip().replace(",", ""))
    except ValueError:
        raise ValueError("Amount must be a number.")
    if not math.isfinite(value) or value <= 0:
        raise ValueError("Amount must be greater than 0.")
    return round(value, 2)


def clean_category(text):
    name = " ".join(str(text).split())
    if not name:
        raise ValueError("Category name cannot be empty.")
    if len(name) > 30:
        raise ValueError("Category name is too long (max 30 characters).")
    return name


class ExpenseDB:
    def __init__(self, path=DB_FILE):
        self.conn = sqlite3.connect(path)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS categories ("
                "name TEXT PRIMARY KEY COLLATE NOCASE)"
            )
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS expenses ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "date TEXT NOT NULL, "
                "amount REAL NOT NULL, "
                "category TEXT NOT NULL, "
                "description TEXT NOT NULL DEFAULT '')"
            )
            self.conn.executemany(
                "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                [(name,) for name in DEFAULT_CATEGORIES],
            )

    def close(self):
        self.conn.close()


    def get_categories(self):
        rows = self.conn.execute("SELECT name FROM categories ORDER BY rowid")
        return [row[0] for row in rows]

    def add_category(self, name):
        name = clean_category(name)
        with self.conn:
            cursor = self.conn.execute(
                "INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,)
            )
        if cursor.rowcount == 0:
            raise ValueError(f"The category '{name}' already exists.")
        return name


    def add_expense(self, date_text, amount_text, category, description=""):
        day = parse_date(date_text)
        amount = parse_amount(amount_text)

        names = {name.lower(): name for name in self.get_categories()}
        key = str(category).strip().lower()
        if key not in names:
            raise ValueError("Please choose a valid category.")

        description = description.strip()
        if len(description) > 100:
            raise ValueError("Description is too long (max 100 characters).")

        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO expenses (date, amount, category, description) "
                "VALUES (?, ?, ?, ?)",
                (day, amount, names[key], description),
            )
        return cursor.lastrowid

    def get_expenses(self, month=None):
        query = "SELECT id, date, amount, category, description FROM expenses"
        params = ()
        if month:
            query += " WHERE substr(date, 1, 7) = ?"
            params = (month,)
        query += " ORDER BY date DESC, id DESC"
        return self.conn.execute(query, params).fetchall()

    def delete_expense(self, expense_id):
        with self.conn:
            cursor = self.conn.execute(
                "DELETE FROM expenses WHERE id = ?", (expense_id,)
            )
        return cursor.rowcount

    def available_months(self):
        rows = self.conn.execute(
            "SELECT DISTINCT substr(date, 1, 7) FROM expenses ORDER BY 1 DESC"
        )
        return [row[0] for row in rows]


    def summary(self, month=None):
        where = ""
        params = ()
        if month:
            where = " WHERE substr(date, 1, 7) = ?"
            params = (month,)

        rows = self.conn.execute(
            "SELECT category, SUM(amount) FROM expenses" + where +
            " GROUP BY category ORDER BY SUM(amount) DESC, category",
            params,
        ).fetchall()
        count = self.conn.execute(
            "SELECT COUNT(*) FROM expenses" + where, params
        ).fetchone()[0]
        biggest = self.conn.execute(
            "SELECT date, amount, category, description FROM expenses" + where +
            " ORDER BY amount DESC, date DESC LIMIT 1",
            params,
        ).fetchone()

        by_category = [(name, round(total, 2)) for name, total in rows]
        total = round(sum(amount for _, amount in by_category), 2)

        return {
            "month": month,
            "total": total,
            "count": count,
            "average": round(total / count, 2) if count else 0,
            "by_category": by_category,
            "top_category": by_category[0] if by_category else None,
            "biggest": biggest,
        }

    def export_csv(self, path, month=None):
        rows = self.get_expenses(month)
        rows.reverse()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Category", "Description", "Amount"])
            for _, day, amount, category, description in rows:
                writer.writerow([day, category, description, f"{amount:.2f}"])
        return len(rows)