# activity_page.py
import tkinter as tk
from PIL import Image, ImageTk
import serial

class ActivityPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1024, height=600, bg="#0032A0")
        self.controller = controller
        self.ser = self.controller.get_serial_port()

        # User info (top-right)
        self.user_id_label = tk.Label(
            self, text="ID: -", font=("Arial", 16), fg="white", bg="#0032A0"
        )
        self.user_id_label.place(relx=1, y=10, anchor="ne", x=-10)

        self.credits_label = tk.Label(
            self, text="Credits: 0", font=("Arial", 16), fg="white", bg="#0032A0"
        )
        self.credits_label.place(relx=1, y=50, anchor="ne", x=-10)

        # Buttons (top-left horizontally)
        btn_style = {"font": ("Arial", 14), "width": 18, "height": 2}

        return_btn = tk.Button(
            self,
            text="Return to Home",
            **btn_style,
            command=lambda: controller.show_frame("HomePage"),
        )
        return_btn.place(x=10, y=10)

        dispense_btn = tk.Button(
            self,
            text="Dispense Hardware",
            **btn_style,
            command=lambda: controller.show_frame("DispenseOrderPage"),
        )
        dispense_btn.place(x=230, y=10)

        sort_btn = tk.Button(
            self,
            text="Sort Hardware",
            **btn_style,
            command=lambda: controller.show_frame("PreSortPage"),
        )
        sort_btn.place(x=450, y=10)

        # White box with thick black border (same as HomePage)
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
            box_frame, text="Select an Activity", font=("Arial", 18), bg="white"
        )
        project_text.place(relx=0.5, rely=0.7, anchor="center")

    def set_user_info(self, user_id, credits):
        self.user_id_label.config(text=f"ID: {user_id}")
        self.credits_label.config(text=f"Credits: {credits}")

    def tkraise(self, aboveThis=None):
        self.set_user_info(
            self.controller.current_user_id, self.controller.current_user_credits
        )
        self.ser.flush()
        self.send_command("sort_early_exit\n")
        super().tkraise(aboveThis)

    def send_command(self, command):
            print(f"Sending {command}")
            self.ser.write(command.encode())
            while True:
                response = self.ser.readline().decode()
                print(response)
                if response == "ACK\n":
                    break
                else:
                    print("STM is not in the sort state, or is an unexpected state")
                    break