import json
import os
import tkinter as tk
from tkinter import messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.join(BASE_DIR, "tasks.json")

BG = "#f4f8fb"
DARK = "#1f3a5f"
GREEN = "#2e9e6b"
RED = "#d64545"
BLUE = "#2f7de1"
GREY = "#8a97a5"


def load_tasks():
    if not os.path.exists(FILE_NAME):
        return []
    try:
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_tasks(tasks):
    with open(FILE_NAME, "w") as f:
        json.dump(tasks, f, indent=4)


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List")
        self.root.geometry("480x560")
        self.root.configure(bg=BG)

        self.tasks = load_tasks()

        self.build_ui()
        self.refresh()

    def build_ui(self):
        tk.Label(
            self.root, text="My To-Do List",
            font=("Segoe UI", 20, "bold"), bg=BG, fg=DARK,
        ).pack(pady=(18, 10))

        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=20)

        self.entry = tk.Entry(top, font=("Segoe UI", 12))
        self.entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.entry.bind("<Return>", lambda event: self.add_task())
        self.entry.focus()

        tk.Button(
            top, text="Add", command=self.add_task,
            bg=BLUE, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=14, pady=4,
        ).pack(side="left", padx=(8, 0))

        list_frame = tk.Frame(self.root, bg=BG)
        list_frame.pack(fill="both", expand=True, padx=20, pady=15)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            list_frame, font=("Segoe UI", 12), activestyle="none",
            selectbackground="#cfe3fb", selectforeground=DARK,
            relief="flat", highlightthickness=1, highlightbackground="#d5e0ea",
            yscrollcommand=scrollbar.set,
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<Double-Button-1>", lambda event: self.toggle_done())

        buttons = tk.Frame(self.root, bg=BG)
        buttons.pack(fill="x", padx=20)

        tk.Button(
            buttons, text="Mark Done / Undo", command=self.toggle_done,
            bg=GREEN, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", pady=6,
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        tk.Button(
            buttons, text="Delete", command=self.delete_task,
            bg=RED, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", pady=6,
        ).pack(side="left", fill="x", expand=True, padx=5)

        tk.Button(
            buttons, text="Clear Completed", command=self.clear_completed,
            bg=GREY, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", pady=6,
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.status = tk.Label(
            self.root, text="", font=("Segoe UI", 10), bg=BG, fg=GREY,
        )
        self.status.pack(pady=12)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for i, task in enumerate(self.tasks):
            mark = "✔" if task["done"] else "○"
            self.listbox.insert(tk.END, f"  {mark}   {task['title']}")
            if task["done"]:
                self.listbox.itemconfig(i, fg=GREY)

        total = len(self.tasks)
        done = sum(1 for task in self.tasks if task["done"])
        self.status.config(
            text=f"{total} tasks  |  {done} completed  |  {total - done} pending"
        )

    def selected_index(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Select a task", "Please click a task first.")
            return None
        return selection[0]

    def add_task(self):
        title = self.entry.get().strip()
        if not title:
            messagebox.showwarning("Empty task", "Please type a task first.")
            return
        self.tasks.append({"title": title, "done": False})
        save_tasks(self.tasks)
        self.entry.delete(0, tk.END)
        self.refresh()
        self.listbox.see(tk.END)

    def toggle_done(self):
        index = self.selected_index()
        if index is None:
            return
        self.tasks[index]["done"] = not self.tasks[index]["done"]
        save_tasks(self.tasks)
        self.refresh()
        self.listbox.selection_set(index)

    def delete_task(self):
        index = self.selected_index()
        if index is None:
            return
        title = self.tasks[index]["title"]
        if messagebox.askyesno("Delete task", f"Delete '{title}'?"):
            self.tasks.pop(index)
            save_tasks(self.tasks)
            self.refresh()

    def clear_completed(self):
        if not any(task["done"] for task in self.tasks):
            messagebox.showinfo("Nothing to clear", "No completed tasks yet.")
            return
        if messagebox.askyesno("Clear completed", "Remove all completed tasks?"):
            self.tasks = [task for task in self.tasks if not task["done"]]
            save_tasks(self.tasks)
            self.refresh()


def main():
    root = tk.Tk()
    TodoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()