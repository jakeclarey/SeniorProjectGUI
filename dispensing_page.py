# dispense_page.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import serial
import threading


class DispensingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1024, height=600, bg="#0032A0")
        self.controller = controller
        self.ser = self.controller.get_serial_port()
        
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
        super().tkraise(aboveThis)
        self.dispensing_thread = threading.Thread(
            target=self.run_dispensing_process, daemon=True
        )
        self.finished = False
        self.dispensing_thread.start()
        self.check_dispensing_finished()

    def check_dispensing_finished(self):
        if self.finished:
            self.after(3000, lambda: self.controller.show_frame("IdlePage"))
        else:
            self.after(500, self.check_dispensing_finished)  # Keep checking every 500ms

    def run_dispensing_process(self):
        self.start_serial_communication()
        return

    def start_serial_communication(self):
        try:
            # Step 2: Send hardware_list.txt content
            with open("hardware_list.txt", "r") as file:
                # Read the parts to be dispensed from the hardware list file, removing new lines.
                data = file.read().strip().replace("\n", "")
                print("dispense{student_order}\n".format(student_order=data))
                # Send dispense; to trigger dispensing state, then send the student's order and terminate with new line.
                self.ser.write("dispense{student_order}\n".format(student_order=data).encode())

            # Step 3: Wait for 'ack', which indicates STM accepts the dispensing request.
            while True:
                response = self.ser.readline().decode().strip().lower()
                if response == "ack":
                    print("[DEBUG] STM32 acknowledged dispense request.")
                    break

            # Step 4: Wait for 'done', which indicates the parts have been dispensed.
            while True:
                print("[DEBUG] Waiting for done from STM")
                response = self.ser.readline().decode().strip().lower()
                if response:
                    print("[DEBUG] Dispense complete.")
                    self.finished = True # What is the point of this?
                    # self.controller.show_frame("IdlePage")
                    break
                else:
                    print("[DEBUG] Done message failed, moving on.")
                    self.finished = True
                    break

        except Exception as e:
            print(f"[ERROR] Serial communication: {e}")
            self.finished = True
