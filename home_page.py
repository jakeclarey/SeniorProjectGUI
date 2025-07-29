# home_page.py
import tkinter as tk
from PIL import Image, ImageTk
import threading
import keycard


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1024, height=600, bg="#0032A0")
        self.controller = controller

        # Scan Keycard button
        keycard_button = tk.Button(
            self,
            text="Scan Keycard",
            font=("Arial", 14),
            width=14,
            height=2,
            command=self.start_keycard_scan,
        )
        keycard_button.place(x=10, y=10)  # Top-left position

        # Admin button
        admin_button = tk.Button(
            self,
            text="Admin",
            font=("Arial", 14),
            width=8,
            height=2,
            command=lambda: controller.show_frame("AdminPwdPage"),
        )
        admin_button.place(relx=1, y=10, anchor="ne", x=-(250))

        # View Available Stock button
        stock_button = tk.Button(
            self,
            text="View Available Stock",
            font=("Arial", 14),
            width=18,
            height=2,
            command=lambda: controller.show_frame("HardwareStockPage"),
        )
        stock_button.place(relx=1, y=10, anchor="ne", x=-10)

        # Status label for scan result
        self.status_label = tk.Label(
            self, text="", font=("Arial", 16), bg="#0032A0", fg="white"
        )
        self.status_label.place(relx=0.5, rely=0.9, anchor="center")

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

    def start_keycard_scan(self):
        """Run the scan function in a separate thread."""
        print("Scan Keycard button pressed")
        self.status_label.config(text="Scanning for keycard...")
        threading.Thread(target=self.run_scan, daemon=True).start()

    def run_scan(self):
        """Call the scan function and update UI when done."""
        result = keycard.scan()  # This will block, so it's in a thread
        result = 3344
        if result:
            # Navigate to ActivityPage
            self.controller.current_user_id = result
            keycard.store_student_id(self.controller.current_user_id)
            self.controller.current_user_credits = keycard.get_user_credits(
                self.controller.current_user_id
            )
            print(f"Timeout did not occur: ID = {self.controller.current_user_id}")
            print(
                f"                       Credits = {self.controller.current_user_credits}"
            )
            self.after(0, lambda: self.controller.show_frame("ActivityPage"))
        else:
            # Show timeout message
            self.controller.current_user_id = None
            self.controller.current_user_credits = None
            print(f"Timeout occured: ID = {self.controller.current_user_id}")
            print(f"                 Credits = {self.controller.current_user_credits}")
            self.after(
                0,
                lambda: self.status_label.config(
                    text="Keycard Timeout - Please Try Again"
                ),
            )

    def tkraise(self, aboveThis=None):
        self.status_label.config(text="")
        self.controller.current_user_id = None
        self.controller.current_user_credits = None
        self.controller.previous_page = "HomePage"
        super().tkraise(aboveThis)
