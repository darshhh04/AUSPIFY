import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox

from chatbot import Chatbot

BG = "#f4f8fb"
HEADER = "#1f3a5f"
BLUE = "#2f7de1"
BOT_BUBBLE = "#e3ecf6"
DARK = "#1f3a5f"
GREY = "#7a8896"

TYPING_DELAY = 450  

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chatbot")
        self.root.geometry("460x660")
        self.root.minsize(380, 480)
        self.root.configure(bg=BG)

        self.bot = Chatbot()
        self.show_debug = tk.BooleanVar(value=False)

        self.build_ui()
        self.add_message("bot", self.bot.greeting())

    def build_ui(self):
        header = tk.Frame(self.root, bg=HEADER)
        header.pack(fill="x")

        title_box = tk.Frame(header, bg=HEADER)
        title_box.pack(side="left", padx=15, pady=10)
        tk.Label(
            title_box, text=f"{self.bot.name}  |  AI Chatbot",
            font=("Segoe UI", 15, "bold"), bg=HEADER, fg="white",
        ).pack(anchor="w")
        tk.Label(
            title_box, text="Online", font=("Segoe UI", 9),
            bg=HEADER, fg="#8fd19e",
        ).pack(anchor="w")

        for text, command in (("Clear", self.clear_chat), ("Save", self.save_chat)):
            tk.Button(
                header, text=text, command=command,
                bg="#2c507f", fg="white", activebackground="#3b6399",
                activeforeground="white", relief="flat",
                font=("Segoe UI", 9, "bold"), padx=10, pady=3,
            ).pack(side="right", padx=(0, 8), pady=14)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(body)
        scrollbar.pack(side="right", fill="y")

        self.chat = tk.Text(
            body, wrap="word", state="disabled", bg=BG, relief="flat",
            font=("Segoe UI", 11), padx=6, pady=8, cursor="arrow",
            highlightthickness=0, yscrollcommand=scrollbar.set,
        )
        self.chat.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.chat.yview)
        self.setup_tags()

        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=12)

        self.status = tk.Label(
            footer, text="", bg=BG, fg=GREY, font=("Segoe UI", 9, "italic"),
        )
        self.status.pack(side="left")

        tk.Checkbutton(
            footer, text="Show intent", variable=self.show_debug,
            bg=BG, fg=GREY, activebackground=BG, font=("Segoe UI", 9),
        ).pack(side="right")

        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=12, pady=(4, 12))

        self.entry = tk.Entry(
            bar, font=("Segoe UI", 12), relief="flat", highlightthickness=1,
            highlightbackground="#c9d6e2", highlightcolor=BLUE,
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.entry.bind("<Return>", lambda event: self.send())
        self.entry.focus()

        tk.Button(
            bar, text="Send", command=self.send,
            bg=BLUE, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=18, pady=6,
        ).pack(side="left", padx=(8, 0))

    def setup_tags(self):
        small = ("Segoe UI", 8)
        self.chat.tag_configure(
            "user_name", justify="right", foreground=GREY, font=small,
            rmargin=12, spacing1=10,
        )
        self.chat.tag_configure(
            "user", justify="right", background=BLUE, foreground="white",
            lmargin1=90, lmargin2=90, rmargin=12, spacing1=2, spacing3=2,
        )
        self.chat.tag_configure(
            "bot_name", justify="left", foreground=GREY, font=small,
            lmargin1=12, lmargin2=12, spacing1=10,
        )
        self.chat.tag_configure(
            "bot", justify="left", background=BOT_BUBBLE, foreground=DARK,
            lmargin1=12, lmargin2=12, rmargin=90, spacing1=2, spacing3=2,
        )
        self.chat.tag_configure(
            "debug", justify="left", foreground=GREY,
            font=("Segoe UI", 8, "italic"), lmargin1=12, lmargin2=12,
        )

    def add_message(self, sender, text, reply=None):
        stamp = datetime.now().strftime("%H:%M")
        label = "You" if sender == "user" else self.bot.name

        self.chat.config(state="normal")
        self.chat.insert("end", f"{label}  {stamp}\n", f"{sender}_name")

        for line in text.split("\n"):
            self.chat.insert("end", f" {line} ", sender)
            self.chat.insert("end", "\n")

        if reply is not None and self.show_debug.get():
            self.chat.insert(
                "end",
                f"intent: {reply.intent}   confidence: {reply.confidence:.2f}\n",
                "debug",
            )

        self.chat.config(state="disabled")
        self.chat.see("end")


    def send(self):
        text = self.entry.get().strip()
        if not text:
            return

        self.entry.delete(0, tk.END)
        self.add_message("user", text)

        reply = self.bot.respond(text)
        self.status.config(text=f"{self.bot.name} is typing...")
        self.root.after(TYPING_DELAY, lambda: self.show_reply(reply))

    def show_reply(self, reply):
        self.status.config(text="")
        self.add_message("bot", reply.text, reply)

    def clear_chat(self):
        self.bot.reset()
        self.chat.config(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.config(state="disabled")
        self.add_message("bot", self.bot.greeting())

    def save_chat(self):
        if not self.bot.history:
            messagebox.showinfo("Nothing to save", "Start a conversation first.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile="chat_history.txt",
            filetypes=[("Text files", "*.txt")],
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                for stamp, speaker, text in self.bot.history:
                    f.write(f"[{stamp}] {speaker}: {text}\n")
        except OSError as error:
            messagebox.showerror("Save failed", f"Could not save the file:\n{error}")
            return
        messagebox.showinfo("Chat saved", f"Conversation saved to:\n{path}")


def main():
    root = tk.Tk()
    ChatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()