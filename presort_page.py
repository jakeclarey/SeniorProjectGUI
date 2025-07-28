# presort_page.py
import tkinter as tk
from PIL import Image, ImageTk
import threading
import reed_utils
import serial


class PreSortPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1024, height=600, bg="#0032A0")
        self.controller = controller

        # Button in top-left corner
        button = tk.Button(
            self,
            text="Return to Activity",
            font=("Arial", 14),
            width=18,
            height=2,
            command=self.sort_early_exit,
        )
        button.place(x=10, y=10)  # Top-left position

        # Button in top-left corner
        button = tk.Button(
            self,
            text="Press to Continue",
            font=("Arial", 14),
            width=18,
            height=2,
            command=self.check_intake_closed,
        )
        button.place(relx=1, y=10, anchor="ne", x=-10)  # Top-right position

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
            text="Please place parts in the intake and close the lid.",
            font=("Arial", 18),
            bg="white",
        )
        project_text.place(relx=0.5, rely=0.7, anchor="center")

        # Status label for scan result
        self.status_label = tk.Label(
            self, text="", font=("Arial", 16), bg="#0032A0", fg="white"
        )
        self.status_label.place(relx=0.5, rely=0.9, anchor="center")

    def start_intake_closed_check(self):
        """Run the scan function in a separate thread."""
        print("Checking intake lid sensor")
        threading.Thread(target=self.check_intake_closed, daemon=True).start()

    def check_intake_closed(self):
        """Call the check reed switch function and if closed go to SortHardwarePage."""
        result = reed_utils.check_lid_sensor()
        if result:
            print("Lid was closed")
            self.after(
                0,
                lambda: self.status_label.config(
                    text="Lid Was Closed - Continuing to Sorting"
                ),
            )
            self.after(1000, lambda: self.controller.show_frame("SortHardwarePage"))
        else:
            print("Lid was open")
            self.after(
                0,
                lambda: self.status_label.config(
                    text="Lid Was Open - Please Close It and Try Again"
                ),
            )

    def tkraise(self, aboveThis=None):
        self.status_label.config(text="")
        self.ser = self.controller.get_serial_port()
        self.ser.flush()
        self.send_command("sort\n")
        super().tkraise(aboveThis)

    def sort_early_exit_command(self):
        print("Sending sort_early_exit")
        self.ser.write("sort_early_exit".encode())
        while True:
            response = self.ser.readline().decode()
            print(response)
            if response == "ACK\n":
                break
            elif response == "NACK\n":
                print("STM is in sort state, or is in an unexpected state.")
                break
        self.controller.show_frame("ActivityPage")

    def send_command(self, command):
        print(f"Sending {command}")
        self.ser.write(command.encode())
        while True:
            response = self.ser.readline().decode()
            print(response)
            if response == "ACK\n":
                break
            elif response == "NACK\n":
                print("STM is in sort state, or is in an unexpected state.")
                break
