import math
import tkinter as tk

BG = "#f4f8fb"
DARK = "#1f3a5f"
BLUE = "#2f7de1"
GREEN = "#2e9e6b"
RED = "#d64545"
GREY = "#8a97a5"
LIGHT = "#ffffff"
SOFT = "#dde6ee"

OPERATORS = ("+", "-", "×", "÷")


def calculate(a, op, b):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "×":
        return a * b
    if op == "÷":
        if b == 0:
            raise ZeroDivisionError("Cannot divide by 0")
        return a / b
    raise ValueError(f"Unknown operator: {op}")


def format_number(value):
    if not math.isfinite(value):
        raise OverflowError("Number too large")
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    return f"{value:.10g}"


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("340x500")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.current = "0"        
        self.stored = None     
        self.operator = None     
        self.start_new = False  
        self.has_error = False

        self.build_ui()
        self.bind_keys()

    def build_ui(self):

        self.history = tk.Label(
            self.root, text="", anchor="e",
            font=("Segoe UI", 11), bg=BG, fg=GREY,
        )
        self.history.pack(fill="x", padx=20, pady=(20, 0))

        self.display = tk.Label(
            self.root, text="0", anchor="e",
            font=("Segoe UI", 34, "bold"), bg=BG, fg=DARK,
        )
        self.display.pack(fill="x", padx=20, pady=(0, 15))

        pad = tk.Frame(self.root, bg=BG)
        pad.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        layout = [
            ["C", "⌫", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["±", "0", ".", "="],
        ]

        for r, row in enumerate(layout):
            pad.rowconfigure(r, weight=1)
            for c, label in enumerate(row):
                pad.columnconfigure(c, weight=1)

                if label in OPERATORS:
                    bg, fg = BLUE, "white"
                elif label == "=":
                    bg, fg = GREEN, "white"
                elif label == "C":
                    bg, fg = RED, "white"
                elif label in ("⌫", "%", "±"):
                    bg, fg = SOFT, DARK
                else:
                    bg, fg = LIGHT, DARK

                tk.Button(
                    pad, text=label, font=("Segoe UI", 16, "bold"),
                    bg=bg, fg=fg, relief="flat",
                    command=lambda key=label: self.on_press(key),
                ).grid(row=r, column=c, sticky="nsew", padx=4, pady=4)

    def bind_keys(self):
        self.root.bind("<Key>", self.on_key)

    def on_key(self, event):
        key = event.char
        if event.keysym in ("Return", "KP_Enter"):
            self.on_press("=")
        elif event.keysym == "BackSpace":
            self.on_press("⌫")
        elif event.keysym == "Escape":
            self.on_press("C")
        elif key == "*":
            self.on_press("×")
        elif key == "/":
            self.on_press("÷")
        elif key and key in "0123456789.+-%=":
            self.on_press(key)

    def on_press(self, key):
        if key.isdigit():
            self.add_digit(key)
        elif key == ".":
            self.add_dot()
        elif key in OPERATORS:
            self.choose_operator(key)
        elif key == "=":
            self.equals()
        elif key == "C":
            self.clear()
        elif key == "⌫":
            self.backspace()
        elif key == "±":
            self.negate()
        elif key == "%":
            self.percent()


    def update_display(self):
        text = "Error" if self.has_error else self.current
        size = 34 if len(text) <= 10 else 22  
        self.display.config(text=text, font=("Segoe UI", size, "bold"))

    def show_error(self, message):
        self.has_error = True
        self.current = "0"
        self.stored = None
        self.operator = None
        self.history.config(text=message)
        self.update_display()


    def add_digit(self, digit):
        if self.has_error:
            self.clear()
        if self.start_new or self.current == "0":
            self.current = digit
            self.start_new = False
        elif len(self.current.replace("-", "").replace(".", "")) < 15:
            self.current += digit
        self.update_display()

    def add_dot(self):
        if self.has_error:
            self.clear()
        if self.start_new:
            self.current = "0."
            self.start_new = False
        elif "." not in self.current:
            self.current += "."
        self.update_display()

    def backspace(self):
        if self.has_error or self.start_new:
            return
        self.current = self.current[:-1]
        if self.current in ("", "-"):
            self.current = "0"
        self.update_display()

    def negate(self):
        if self.has_error or self.current == "0":
            return
        if self.current.startswith("-"):
            self.current = self.current[1:]
        else:
            self.current = "-" + self.current
        self.update_display()

    def percent(self):
        if self.has_error:
            return
        self.current = format_number(float(self.current) / 100)
        self.start_new = True
        self.update_display()


    def compute(self):
        try:
            result = calculate(self.stored, self.operator, float(self.current))
            self.current = format_number(result)
        except ZeroDivisionError:
            self.show_error("Cannot divide by 0")
            return False
        except (OverflowError, ValueError):
            self.show_error("Invalid input")
            return False
        return True

    def choose_operator(self, op):
        if self.has_error:
            return
        if self.operator and not self.start_new:
            if not self.compute():
                return
        self.stored = float(self.current)
        self.operator = op
        self.start_new = True
        self.history.config(text=f"{format_number(self.stored)} {op}")
        self.update_display()

    def equals(self):
        if self.has_error or self.operator is None:
            return
        left = self.stored
        op = self.operator
        right = float(self.current)

        if self.compute():
            self.history.config(
                text=f"{format_number(left)} {op} {format_number(right)} ="
            )
        self.stored = None
        self.operator = None
        self.start_new = True
        self.update_display()

    def clear(self):
        self.current = "0"
        self.stored = None
        self.operator = None
        self.start_new = False
        self.has_error = False
        self.history.config(text="")
        self.update_display()


def main():
    root = tk.Tk()
    CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()