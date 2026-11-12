import tkinter as tk
from datetime import date
from tkinter import filedialog, messagebox, simpledialog, ttk

from expense_db import ExpenseDB

BG = "#f4f8fb"
CARD = "#ffffff"
DARK = "#1f3a5f"
BLUE = "#2f7de1"
GREEN = "#2e9e6b"
RED = "#d64545"
GREY = "#6f7f90"
BORDER = "#d5e0ea"
BAR_COLORS = [
    "#2f7de1", "#2e9e6b", "#f0a030", "#d64545",
    "#8e5fd6", "#17a2b8", "#e0699b", "#7c8b99",
]

ALL_TIME = "All time"


def money(value):
    return f"₹{value:,.2f}"


class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("780x680")
        self.root.minsize(720, 600)
        self.root.configure(bg=BG)

        self.db = ExpenseDB()

        self.setup_style()
        self.build_ui()
        self.refresh_all()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.db.close()
        self.root.destroy()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TNotebook.Tab", font=("Segoe UI", 11), padding=(14, 6))

    def build_ui(self):
        tk.Label(
            self.root, text="Expense Tracker",
            font=("Segoe UI", 20, "bold"), bg=BG, fg=DARK,
        ).pack(pady=(15, 5))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        self.expenses_tab = tk.Frame(self.notebook, bg=BG)
        self.reports_tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(self.expenses_tab, text="Expenses")
        self.notebook.add(self.reports_tab, text="Reports")

        self.build_expenses_tab()
        self.build_reports_tab()

        self.notebook.bind("<<NotebookTabChanged>>", lambda event: self.refresh_report())

    def build_expenses_tab(self):
        tab = self.expenses_tab

        form = tk.LabelFrame(
            tab, text=" Add expense ", bg=BG, fg=DARK,
            font=("Segoe UI", 10, "bold"), padx=12, pady=8,
        )
        form.pack(fill="x", padx=15, pady=(15, 8))
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        label_font = ("Segoe UI", 9)

        tk.Label(form, text="Date (YYYY-MM-DD)", bg=BG, fg=GREY, font=label_font).grid(row=0, column=0, sticky="w")
        self.date_entry = tk.Entry(form, font=("Segoe UI", 11))
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 6), ipady=3)

        tk.Label(form, text="Amount (₹)", bg=BG, fg=GREY, font=label_font).grid(row=0, column=1, sticky="w")
        self.amount_entry = tk.Entry(form, font=("Segoe UI", 11))
        self.amount_entry.grid(row=1, column=1, sticky="ew", pady=(0, 6), ipady=3)

        tk.Label(form, text="Category", bg=BG, fg=GREY, font=label_font).grid(row=2, column=0, sticky="w")
        category_row = tk.Frame(form, bg=BG)
        category_row.grid(row=3, column=0, sticky="ew", padx=(0, 10), pady=(0, 8))
        categories = self.db.get_categories()
        self.category_box = ttk.Combobox(
            category_row, values=categories, state="readonly", font=("Segoe UI", 11),
        )
        self.category_box.set(categories[0])
        self.category_box.pack(side="left", fill="x", expand=True)
        tk.Button(
            category_row, text="+", command=self.add_category,
            bg=GREEN, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", width=3,
        ).pack(side="left", padx=(6, 0))

        tk.Label(form, text="Description (optional)", bg=BG, fg=GREY, font=label_font).grid(row=2, column=1, sticky="w")
        self.desc_entry = tk.Entry(form, font=("Segoe UI", 11))
        self.desc_entry.grid(row=3, column=1, sticky="ew", pady=(0, 8), ipady=3)

        tk.Button(
            form, text="Add Expense", command=self.add_expense,
            bg=BLUE, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", pady=5,
        ).grid(row=4, column=0, columnspan=2, sticky="ew")

        for entry in (self.date_entry, self.amount_entry, self.desc_entry):
            entry.bind("<Return>", lambda event: self.add_expense())

        bar = tk.Frame(tab, bg=BG)
        bar.pack(fill="x", padx=15)

        tk.Label(bar, text="Show:", bg=BG, fg=DARK, font=("Segoe UI", 10)).pack(side="left")
        self.filter_box = ttk.Combobox(bar, state="readonly", width=14)
        self.filter_box.pack(side="left", padx=6)
        self.filter_box.bind("<<ComboboxSelected>>", lambda event: self.refresh_expenses())

        self.list_total = tk.Label(bar, text="", bg=BG, fg=DARK, font=("Segoe UI", 10, "bold"))
        self.list_total.pack(side="right")

        table = tk.Frame(tab, bg=BG)
        table.pack(fill="both", expand=True, padx=15, pady=8)

        columns = ("date", "category", "description", "amount")
        self.tree = ttk.Treeview(table, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("date", text="Date")
        self.tree.heading("category", text="Category")
        self.tree.heading("description", text="Description")
        self.tree.heading("amount", text="Amount")
        self.tree.column("date", width=95, stretch=False)
        self.tree.column("category", width=110, stretch=False)
        self.tree.column("description", width=250)
        self.tree.column("amount", width=100, anchor="e", stretch=False)

        scrollbar = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        tk.Button(
            tab, text="Delete Selected", command=self.delete_expense,
            bg=RED, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=14, pady=5,
        ).pack(pady=(0, 12))

    def build_reports_tab(self):
        tab = self.reports_tab

        top = tk.Frame(tab, bg=BG)
        top.pack(fill="x", padx=15, pady=15)

        tk.Label(top, text="Report for:", bg=BG, fg=DARK, font=("Segoe UI", 11)).pack(side="left")
        self.report_box = ttk.Combobox(top, state="readonly", width=14)
        self.report_box.pack(side="left", padx=8)
        self.report_box.bind("<<ComboboxSelected>>", lambda event: self.refresh_report())

        tk.Button(
            top, text="Export to CSV", command=self.export_csv,
            bg=BLUE, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=12, pady=4,
        ).pack(side="right")

        cards = tk.Frame(tab, bg=BG)
        cards.pack(fill="x", padx=15)
        for column in range(4):
            cards.columnconfigure(column, weight=1)

        self.total_value = self.make_card(cards, "Total spent", 0)
        self.count_value = self.make_card(cards, "Expenses", 1)
        self.average_value = self.make_card(cards, "Average per expense", 2)
        self.top_value = self.make_card(cards, "Top category", 3)

        self.biggest_label = tk.Label(
            tab, text="", bg=BG, fg=GREY, font=("Segoe UI", 10),
            anchor="w", wraplength=700, justify="left",
        )
        self.biggest_label.pack(fill="x", padx=15, pady=(12, 0))

        tk.Label(
            tab, text="Spending by category", bg=BG, fg=DARK,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=15, pady=(14, 0))

        chart_frame = tk.Frame(tab, bg=BG)
        chart_frame.pack(fill="both", expand=True, padx=15, pady=(6, 15))

        chart_scroll = ttk.Scrollbar(chart_frame, orient="vertical")
        chart_scroll.pack(side="right", fill="y")
        self.chart = tk.Canvas(
            chart_frame, bg=CARD, highlightthickness=1,
            highlightbackground=BORDER, yscrollcommand=chart_scroll.set,
        )
        self.chart.pack(side="left", fill="both", expand=True)
        chart_scroll.config(command=self.chart.yview)

    def make_card(self, parent, title, column):
        card = tk.Frame(parent, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        card.grid(row=0, column=column, sticky="nsew", padx=4)
        tk.Label(card, text=title, bg=CARD, fg=GREY, font=("Segoe UI", 9)).pack(pady=(10, 0))
        value = tk.Label(card, text="--", bg=CARD, fg=DARK, font=("Segoe UI", 14, "bold"))
        value.pack(pady=(2, 10), padx=6)
        return value


    def selected_month(self, box):
        value = box.get()
        return None if value in ("", ALL_TIME) else value

    def refresh_all(self):
        self.refresh_months()
        self.refresh_expenses()
        self.refresh_report()

    def refresh_months(self):
        months = self.db.available_months()
        values = [ALL_TIME] + months

        self.filter_box["values"] = values
        if self.filter_box.get() not in values:
            self.filter_box.set(ALL_TIME)

        self.report_box["values"] = values
        if self.report_box.get() not in values:
            self.report_box.set(months[0] if months else ALL_TIME)

    def refresh_expenses(self):
        rows = self.db.get_expenses(self.selected_month(self.filter_box))

        self.tree.delete(*self.tree.get_children())
        for expense_id, day, amount, category, description in rows:
            self.tree.insert(
                "", "end", iid=str(expense_id),
                values=(day, category, description, money(amount)),
            )

        total = round(sum(row[2] for row in rows), 2)
        self.list_total.config(text=f"{len(rows)} expenses  |  Total {money(total)}")

    def refresh_report(self):
        data = self.db.summary(self.selected_month(self.report_box))

        self.total_value.config(text=money(data["total"]))
        self.count_value.config(text=str(data["count"]))
        self.average_value.config(text=money(data["average"]))
        self.top_value.config(
            text=data["top_category"][0] if data["top_category"] else "--"
        )

        if data["biggest"]:
            day, amount, category, description = data["biggest"]
            extra = f" ({description})" if description else ""
            self.biggest_label.config(
                text=f"Biggest expense: {money(amount)} on {day}, {category}{extra}"
            )
        else:
            self.biggest_label.config(text="No expenses recorded for this period.")

        self.draw_chart(data)

    def draw_chart(self, data):
        self.chart.delete("all")
        items = data["by_category"]

        if not items:
            self.chart.create_text(
                20, 25, text="Nothing to show yet.", anchor="w",
                fill=GREY, font=("Segoe UI", 11),
            )
            self.chart.config(scrollregion=(0, 0, 0, 0))
            return

        largest = items[0][1]
        total = data["total"]
        row_height = 36
        max_bar = 280

        for i, (name, amount) in enumerate(items):
            y = 22 + i * row_height
            width = max(4, int(amount / largest * max_bar))
            percent = amount / total * 100
            color = BAR_COLORS[i % len(BAR_COLORS)]

            self.chart.create_text(
                15, y, text=name, anchor="w", fill=DARK, font=("Segoe UI", 11),
            )
            self.chart.create_rectangle(
                130, y - 11, 130 + width, y + 11, fill=color, outline="",
            )
            self.chart.create_text(
                130 + width + 10, y, text=f"{money(amount)}  ({percent:.0f}%)",
                anchor="w", fill=DARK, font=("Segoe UI", 10),
            )

        self.chart.config(scrollregion=(0, 0, 0, 22 + len(items) * row_height))

    def add_expense(self):
        try:
            self.db.add_expense(
                self.date_entry.get(),
                self.amount_entry.get(),
                self.category_box.get(),
                self.desc_entry.get(),
            )
        except ValueError as error:
            messagebox.showwarning("Cannot add expense", str(error))
            return

        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.amount_entry.focus()
        self.refresh_all()

    def add_category(self):
        name = simpledialog.askstring("New category", "Category name:", parent=self.root)
        if name is None:
            return
        try:
            saved = self.db.add_category(name)
        except ValueError as error:
            messagebox.showwarning("Cannot add category", str(error))
            return
        self.category_box["values"] = self.db.get_categories()
        self.category_box.set(saved)

    def delete_expense(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Select an expense", "Please click an expense first.")
            return
        if messagebox.askyesno("Delete expense", "Delete the selected expense?"):
            self.db.delete_expense(int(selection[0]))
            self.refresh_all()

    def export_csv(self):
        month = self.selected_month(self.report_box)
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"expenses_{month or 'all'}.csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        try:
            count = self.db.export_csv(path, month)
        except OSError as error:
            messagebox.showerror("Export failed", f"Could not save the file:\n{error}")
            return
        messagebox.showinfo("Export complete", f"Saved {count} expenses to:\n{path}")


def main():
    root = tk.Tk()
    ExpenseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()