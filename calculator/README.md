# Calculator with GUI

**Auspify Internship | Task 3 (Medium)**

A graphical calculator built with Python and Tkinter. It supports basic arithmetic, shows results as you go, and handles invalid input without crashing.

## What it does

- Basic operations: addition, subtraction, multiplication and division
- Extra buttons: clear (C), backspace (⌫), percent (%) and plus/minus (±)
- Chained calculations, for example `2 + 3 + 4 =` gives 9
- A small line above the result shows the running expression
- Works with the mouse and the keyboard
- Error handling for divide by zero and invalid or oversized numbers
- Long numbers shrink to fit the screen

## Skills used

- Tkinter GUI (frames, labels, buttons, grid layout)
- Event handling (button clicks and key presses)
- Python functions and error handling (`try` / `except`)

## How to run

1. Make sure Python 3.8 or higher is installed.
2. Open a terminal in this folder.
3. Run:

```bash
python calculator.py
```

No extra libraries are needed. On Linux, install Tkinter with `sudo apt install python3-tk` if it is missing.

## Keyboard shortcuts

| Key | Action |
|-----|--------|
| `0-9` and `.` | Type a number |
| `+` `-` `*` `/` | Operators |
| `Enter` or `=` | Show the result |
| `Backspace` | Delete the last digit |
| `Esc` | Clear everything |

## Testing

The calculation logic is kept in separate functions so it can be tested. To run the tests:

```bash
python -m unittest -v
```

Manual checks I did on the interface:

| Input | Expected result |
|-------|-----------------|
| `2 + 3 =` | 5 |
| `2 + 3 + 4 =` | 9 |
| `12 × 3 =` | 36 |
| `9 ÷ 0 =` | Error: Cannot divide by 0 |
| `0.1 + 0.2 =` | 0.3 |
| `5 ± + 2 =` | -3 |
| `50 %` | 0.5 |
| `1.5.5` | 1.55 (second dot is ignored) |
| Press a digit after an error | Calculator resets and starts fresh |

## How it works

The calculator keeps four pieces of state: the number being typed, the stored first number, the chosen operator, and a flag that tells it to start a new number on the next key press. Every button calls one handler, `on_press`, which sends the key to the right method. The actual maths lives in `calculate()`, which raises an error for divide by zero, and the app catches it and shows a message.

## Project structure

```
task3-calculator/
├── calculator.py
├── test_calculator.py
└── README.md
```

## Author

Darshan, Auspify Internship