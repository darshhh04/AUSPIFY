# Expense Tracker System

**Auspify Internship | Task 5 (Advanced)**

A Python desktop application to record daily expenses, sort them into categories, and see spending summaries and monthly reports. Data is stored in a local SQLite database.

## What it does

- Add expenses with a date, amount, category and optional description
- Eight built-in categories, and you can add your own
- All expenses are saved in an SQLite database, so they are still there next time
- Filter the expense list by month
- Delete expenses you entered by mistake
- Monthly report with total spent, number of expenses, average per expense, top category and biggest expense
- Bar chart showing how spending is split across categories
- Export any month (or all expenses) to a CSV file
- Input checks for wrong dates, wrong amounts, empty or duplicate categories

## Skills used

- SQLite database handling (`sqlite3`)
- CSV file handling (`csv`)
- Data processing with SQL grouping and totals
- File management
- Tkinter GUI (tabs, tables, canvas drawing)

## How to run

1. Make sure Python 3.8 or higher is installed.
2. Open a terminal in this folder.
3. Run:

```bash
python expense_app.py
```

No extra libraries are needed. On Linux, install Tkinter with `sudo apt install python3-tk` if it is missing.

The database file `expenses.db` is created automatically in this folder on the first run.

## How to use

| Action | How |
|--------|-----|
| Add an expense | Fill the form on the **Expenses** tab and click **Add Expense** (or press Enter) |
| Add a new category | Click the green **+** next to the category box |
| See only one month | Use the **Show** box above the table |
| Delete an expense | Select it in the table and click **Delete Selected** |
| See a monthly report | Open the **Reports** tab and pick a month |
| Export to CSV | On the **Reports** tab, click **Export to CSV** |

## Database design

Two tables:

| Table | Columns |
|-------|---------|
| `categories` | `name` (primary key, not case sensitive) |
| `expenses` | `id`, `date` (YYYY-MM-DD), `amount`, `category`, `description` |

Dates are stored as `YYYY-MM-DD` text, so a month is found by comparing the first 7 characters (for example `2026-11`). Totals are calculated with SQL `SUM` and `GROUP BY` and rounded to 2 decimals.

## Testing

All the database and calculation code is in `expense_db.py`, separate from the window, so it can be tested without opening the app. The tests use a temporary in-memory database:

```bash
python -m unittest -v
```

Manual checks on the interface:

| Action | Expected result |
|--------|-----------------|
| Add `250` under Food | Appears at the top of the table, total updates |
| Amount `abc`, `0` or `-5` | Warning message, nothing saved |
| Date `12/11/2026` | Warning: date must be in YYYY-MM-DD format |
| Add category `food` | Warning: category already exists |
| Select a month in **Show** | Only that month's expenses are listed |
| Open **Reports** | Cards and bar chart match the table |
| Delete an expense | Table, totals and chart update |
| Export to CSV, open in Excel | Rows are in date order with a header |
| Close and reopen the app | All expenses are still there |

## Project structure

```
task5-expense-tracker/
├── expense_app.py        (the window)
├── expense_db.py         (database, checks, reports, CSV export)
├── test_expense_db.py    (unit tests)
├── expenses.db           (created automatically on first run)
└── README.md
```

## Author

Darshan, Auspify Internship