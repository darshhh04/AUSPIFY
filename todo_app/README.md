# To-Do List Application

**Auspify Internship | Task 2 (Easy)**

A Python desktop application with a simple window interface to manage daily tasks. Tasks are saved to a file, so they are still there the next time you open the app.

## What it does

- Add new tasks (type and press Enter or click Add)
- View all tasks in a scrollable list
- Mark tasks as completed, or undo it (button or double-click)
- Delete unwanted tasks, with a confirmation prompt
- Clear all completed tasks in one click
- Show a live count of total, completed and pending tasks
- Save every change automatically to `tasks.json`

## Skills used

- File handling (reading and writing JSON)
- Lists and dictionaries
- CRUD operations (Create, Read, Update, Delete)
- GUI building with `tkinter`

## How to run

1. Make sure Python 3.8 or higher is installed.
2. Open a terminal in this folder.
3. Run:

```bash
python todo_app.py
```

No extra libraries are needed. `tkinter` comes with Python on Windows and macOS. On Linux, install it with `sudo apt install python3-tk` if it is missing.

## How to use

| Action | How |
|--------|-----|
| Add a task | Type in the box and press Enter, or click **Add** |
| Complete a task | Select it, then click **Mark Done / Undo** (or double-click it) |
| Delete a task | Select it, then click **Delete** |
| Remove all finished tasks | Click **Clear Completed** |

## How it works

Each task is stored as a dictionary, for example `{"title": "Buy milk", "done": false}`. All tasks live in a list. After every add, update or delete, the list is written to `tasks.json`. When the app starts, it loads that file again.

## Project structure

```
task2-todo-list/
├── todo_app.py
├── tasks.json      (created automatically on first run)
└── README.md
```

## Author

Darshan, Auspify Internship