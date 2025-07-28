# dispense_loading_page.py
import tkinter as tk
from PIL import Image, ImageTk
import serial
import time
import keycard


class DispenseLoadingPage(tk.Frame):
    def __init__(self):
        super().__init__(parent, width=1024, height=600, bg="#0032A0")
        self.title("Dispensing...")
        self.configure(bg="#0032A0")
        self.geometry("1024x600")
        self.resizable(False, False)
        self.finished = False

        # Top user info
        self.user_id = keycard.current_user_id
        self.credits = keycard.get_user_credits(self.user_id)

        user_id_decimal = (
            int(self.user_id) if isinstance(self.user_id, str) else self.user_id
        )

        user_info_frame = tk.Frame(self, bg="#598baf")
        user_info_frame.pack(fill="x")

        tk.Label(
            user_info_frame,
            text=f"User ID: {user_id_decimal}",
            font=("Helvetica", 14),
            bg="#598baf",
            fg="black",
        ).pack(side="left", padx=20, pady=5)

        self.credits_label = tk.Label(
            user_info_frame,
            text=f"Credits: {self.credits}",
            font=("Helvetica", 14),
            bg="#598baf",
            fg="black",
        )
        self.credits_label.pack(side="right", padx=20, pady=5)

        # Center canvas area
        canvas = tk.Canvas(
            self, width=1024, height=540, bg="#0032A0", highlightthickness=0
        )
        canvas.pack()

        # Draw white box with thick black border
        canvas.create_rectangle(90, 90, 934, 585, outline="black", width=25)
        canvas.create_rectangle(100, 100, 924, 575, fill="white", outline="white")

        # Load and display GVSU logo
        try:
            logo = Image.open("GVSU_LOGO.png").resize((200, 100))
            self.logo_img = ImageTk.PhotoImage(logo)
            canvas.create_image(512, 450, image=self.logo_img)
        except FileNotFoundError:
            canvas.create_text(
                512, 450, text="LOGO NOT FOUND", font=("Arial", 16), fill="black"
            )

        # Message
        message = "Please Wait While System Processes Order"
        canvas.create_text(
            512, 200, text=message, font=("Montserrat", 20), fill="black"
        )

        self.update()  # Force draw
        self.after(500, self.start_serial_communication)

    def start_serial_communication(self):
        try:
            time.sleep(2)  # Wait before opening serial
            self.ser = serial.Serial("/dev/ttyACM0", 38400, timeout=2)
            time.sleep(2)

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

        self.destroy()  # Close window after finishing
