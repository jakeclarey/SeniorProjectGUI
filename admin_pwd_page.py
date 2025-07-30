# admin_pwd_page.py
import tkinter as tk
from PIL import Image, ImageTk


class AdminPwdPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1024, height=600, bg="#0032A0")
        self.controller = controller
        self.entered_password = ""

        # Title
        title_label = tk.Label(
            self, text="Admin Login", font=("Arial", 28), fg="white", bg="#0032A0"
        )
        title_label.place(relx=0.5, y=50, anchor="center")

        # Instruction label
        password_label = tk.Label(
            self,
            text="Enter Admin Password:",
            font=("Arial", 18),
            fg="white",
            bg="#0032A0",
        )
        password_label.place(relx=0.5, rely=0.2, anchor="center")

        # Password display (masked)
        self.password_display = tk.Label(
            self, text="", font=("Arial", 32), fg="white", bg="#0032A0"
        )
        self.password_display.place(relx=0.5, rely=0.3, anchor="center")

        # Keypad frame
        keypad_frame = tk.Frame(self, bg="#0032A0")
        keypad_frame.place(relx=0.5, rely=0.65, anchor="center")

        # Keypad buttons
        buttons = [
            ("1", 0, 0),
            ("2", 0, 1),
            ("3", 0, 2),
            ("4", 1, 0),
            ("5", 1, 1),
            ("6", 1, 2),
            ("7", 2, 0),
            ("8", 2, 1),
            ("9", 2, 2),
            ("Clear", 3, 0),
            ("0", 3, 1),
            ("Submit", 3, 2),
        ]

        for text, row, col in buttons:
            if text == "Clear":
                cmd = self.clear_password
            elif text == "Submit":
                cmd = self.check_password
            else:
                cmd = lambda t=text: self.add_digit(t)

            btn = tk.Button(
                keypad_frame,
                text=text,
                font=("Arial", 18),
                width=6,
                height=2,
                command=cmd,
            )
            btn.grid(row=row, column=col, padx=10, pady=10)

        # Back button
        back_button = tk.Button(
            self,
            text="Back",
            font=("Arial", 14),
            width=8,
            height=2,
            command=lambda: controller.show_frame("HomePage"),
        )
        back_button.place(x=10, y=10)

    def add_digit(self, digit):
        self.entered_password += digit
        self.password_display.config(text="*" * len(self.entered_password))

    def clear_password(self):
        self.entered_password = ""
        self.password_display.config(text="")

    def check_password(self):
        correct_password = "0000"  # Hardcoded for now
        if self.entered_password == correct_password:
            self.after(0, lambda: self.controller.show_frame("AdminMenuPage"))
        else:
            self.clear_password()

    def tkraise(self, aboveThis=None):
        self.clear_password()
        super().tkraise(aboveThis)
