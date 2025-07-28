# idle_page.py
import tkinter as tk
from PIL import Image, ImageTk


class IdlePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1024, height=600, bg="#0032A0")
        self.controller = controller

        # Button in top-left corner
        button = tk.Button(
            self,
            text="Press to Continue",
            font=("Arial", 14),
            width=18,
            height=2,
            command=lambda: controller.show_frame("HomePage"),
        )
        button.place(x=10, y=10)  # Top-left position

        # White box with thick black border
        box_frame = tk.Frame(
            self, bg="white", highlightbackground="black", highlightthickness=25
        )
        box_frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=400)

        # Load and display image inside the box
        logo_path = "GVSU_LOGO.png"  # Ensure this path is correct
        try:
            logo = Image.open(logo_path)
            self.photo = ImageTk.PhotoImage(logo)
            logo_label = tk.Label(box_frame, image=self.photo, bg="white")
            logo_label.place(relx=0.5, rely=0.3, anchor="center")
        except FileNotFoundError:
            tk.Label(
                box_frame, text="Image Not Found", font=("Arial", 18), bg="white"
            ).place(relx=0.5, rely=0.3, anchor="center")

        # Text below the image inside the box
        project_text = tk.Label(
            box_frame,
            text="Hardware Sorting and Dispense",
            font=("Arial", 18),
            bg="white",
        )
        project_text.place(relx=0.5, rely=0.7, anchor="center")
