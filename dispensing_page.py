# dispense_loading_page.py
import tkinter as tk
from PIL import Image, ImageTk
import serial
import threading


class DispensingPage(tk.Frame):
    def __init__(self, parent, controller):
        def __init__(self, parent, controller):
            super().__init__(parent, width=1024, height=600, bg="#0032A0")
            self.controller = controller

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
                text="Dispensing your order...",
                font=("Arial", 18),
                bg="white",
            )
            project_text.place(relx=0.5, rely=0.7, anchor="center")

    def set_user_info(self, user_id, credits):
        self.user_id_label.config(text=f"ID: {user_id}")
        self.credits_label.config(text=f"Credits: {credits}")

    def tkraise(self, aboveThis=None):
        self.session_credits = 0
        self.set_user_info(
            self.controller.current_user_id, self.controller.current_user_credits
        )
        super().tkraise(aboveThis)
        self.dispensing_thread = threading.Thread(
            target=self.run_dispensing_process, daemon=True
        )
        self.dispensing_thread.start()

    def run_dispensing_process(self):
        return

    def start_serial_communication(self):
        try:
            # Step 1: Send 'dispense;' trigger
            self.ser.write(b"dispense;")

            # Step 2: Send hardware_list.txt content
            with open("hardware_list.txt", "r") as file:
                data = file.read().strip().replace("\n", "")
                self.ser.write(data.encode())
                self.ser.write(b"\n")

            # Step 3: Wait for 'ack'
            while True:
                response = self.ser.readline().decode().strip().lower()
                if response == "ack":
                    print("[DEBUG] STM32 acknowledged.")
                    break

            # Step 4: Wait for 'done'
            while True:
                response = self.ser.readline().decode().strip().lower()
                if response == "done":
                    print("[DEBUG] Dispense complete.")
                    self.finished = True
                    break

        except Exception as e:
            print(f"[ERROR] Serial communication: {e}")
            self.finished = True
