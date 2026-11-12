import csv
import os
import tempfile
import unittest

from expense_db import ExpenseDB, parse_amount, parse_date


class TestInputChecks(unittest.TestCase):
    def test_valid_date(self):
        self.assertEqual(parse_date("2026-11-12"), "2026-11-12")
        self.assertEqual(parse_date("  2026-01-05 "), "2026-01-05")

    def test_invalid_dates(self):
        for bad in ("12/11/2026", "2026-13-45", "yesterday", ""):
            with self.assertRaises(ValueError):
                parse_date(bad)

    def test_valid_amounts(self):
        self.assertEqual(parse_amount("250"), 250.0)
        self.assertEqual(parse_amount("1,250.50"), 1250.5)
        self.assertEqual(parse_amount("9.999"), 10.0)

    def test_invalid_amounts(self):
        for bad in ("abc", "", "0", "-5", "nan", "inf"):
            with self.assertRaises(ValueError):
                parse_amount(bad)


class TestExpenseDB(unittest.TestCase):
    def setUp(self):
        self.db = ExpenseDB(":memory:") 

    def tearDown(self):
        self.db.close()

    def add_sample_data(self):
        self.db.add_expense("2026-10-05", "500", "Food", "Groceries")
        self.db.add_expense("2026-10-20", "1,500.50", "Bills", "Electricity")
        self.db.add_expense("2026-10-21", "250", "Food", "Dinner")
        self.db.add_expense("2026-11-02", "100", "Transport", "Auto")

    # --- categories ---

    def test_default_categories_exist(self):
        categories = self.db.get_categories()
        self.assertIn("Food", categories)
        self.assertEqual(categories[-1], "Other")

    def test_add_category(self):
        self.assertEqual(self.db.add_category("  Pets  "), "Pets")
        self.assertIn("Pets", self.db.get_categories())

    def test_duplicate_category_ignores_case(self):
        with self.assertRaises(ValueError):
            self.db.add_category("food")

    def test_empty_category(self):
        with self.assertRaises(ValueError):
            self.db.add_category("   ")


    def test_add_and_list_newest_first(self):
        self.add_sample_data()
        rows = self.db.get_expenses()
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0][1], "2026-11-02")  
        self.assertEqual(rows[-1][1], "2026-10-05")

    def test_unknown_category_rejected(self):
        with self.assertRaises(ValueError):
            self.db.add_expense("2026-11-01", "50", "Spaceships")

    def test_category_case_is_fixed_when_saving(self):
        self.db.add_expense("2026-11-01", "50", "food")
        self.assertEqual(self.db.get_expenses()[0][3], "Food")

    def test_bad_values_rejected(self):
        with self.assertRaises(ValueError):
            self.db.add_expense("not-a-date", "50", "Food")
        with self.assertRaises(ValueError):
            self.db.add_expense("2026-11-01", "-50", "Food")
        with self.assertRaises(ValueError):
            self.db.add_expense("2026-11-01", "50", "Food", "x" * 101)
        self.assertEqual(self.db.get_expenses(), [])

    def test_month_filter(self):
        self.add_sample_data()
        self.assertEqual(len(self.db.get_expenses("2026-10")), 3)
        self.assertEqual(len(self.db.get_expenses("2026-11")), 1)
        self.assertEqual(self.db.get_expenses("2025-01"), [])

    def test_available_months(self):
        self.add_sample_data()
        self.assertEqual(self.db.available_months(), ["2026-11", "2026-10"])

    def test_delete(self):
        expense_id = self.db.add_expense("2026-11-01", "50", "Food")
        self.assertEqual(self.db.delete_expense(expense_id), 1)
        self.assertEqual(self.db.get_expenses(), [])
        self.assertEqual(self.db.delete_expense(expense_id), 0)  # already gone


    def test_monthly_summary(self):
        self.add_sample_data()
        summary = self.db.summary("2026-10")
        self.assertEqual(summary["total"], 2250.5)
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["average"], 750.17)
        self.assertEqual(summary["by_category"], [("Bills", 1500.5), ("Food", 750.0)])
        self.assertEqual(summary["top_category"], ("Bills", 1500.5))
        self.assertEqual(
            summary["biggest"], ("2026-10-20", 1500.5, "Bills", "Electricity")
        )

    def test_all_time_summary(self):
        self.add_sample_data()
        summary = self.db.summary()
        self.assertEqual(summary["total"], 2350.5)
        self.assertEqual(summary["count"], 4)

    def test_empty_summary(self):
        summary = self.db.summary("2026-01")
        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["count"], 0)
        self.assertEqual(summary["average"], 0)
        self.assertEqual(summary["by_category"], [])
        self.assertIsNone(summary["top_category"])
        self.assertIsNone(summary["biggest"])

    def test_total_has_no_float_error(self):
        self.db.add_expense("2026-11-01", "0.1", "Food")
        self.db.add_expense("2026-11-01", "0.2", "Food")
        self.assertEqual(self.db.summary("2026-11")["total"], 0.3)


    def test_export_csv(self):
        self.add_sample_data()
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "out.csv")
            count = self.db.export_csv(path, "2026-10")
            with open(path, newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))

        self.assertEqual(count, 3)
        self.assertEqual(rows[0], ["Date", "Category", "Description", "Amount"])
        self.assertEqual(rows[1], ["2026-10-05", "Food", "Groceries", "500.00"])  # oldest first
        self.assertEqual(len(rows), 4)


if __name__ == "__main__":
    unittest.main()