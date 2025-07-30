# main.py
import tkinter as tk
from idle_page import IdlePage
from home_page import HomePage
from hardware_stock_page import HardwareStockPage
from admin_pwd_page import AdminPwdPage
from admin_menu_page import AdminMenuPage
from activity_page import ActivityPage
from presort_page import PreSortPage
from sort_hardware_page import SortHardwarePage
from dispense_order_page import DispenseOrderPage
from dispensing_page import DispensingPage

from PIL import Image, ImageTk

import serial
from led_utils import update_inventory_leds


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hardware Sorting System")
        # self.geometry("1024x600")
        self.attributes("-fullscreen", True)

        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.current_user_id = None
        self.current_user_credits = None

        self.serial_port = None
        self.serial_port_init("/dev/ttyACM0", baudrate=38400, timeout=None)
        self.ser = self.get_serial_port()
        self.ser.flush()

        # Default previous page to the IdlePage
        self.previous_page = "IdlePage"

        self.frames = {}

        for PageClass in (
            IdlePage,
            HomePage,
            HardwareStockPage,
            AdminPwdPage,
            AdminMenuPage,
            ActivityPage,
            PreSortPage,
            SortHardwarePage,
            DispenseOrderPage,
            DispensingPage,
            PageOne,
        ):
            page_name = PageClass.__name__
            frame = PageClass(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("IdlePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

        update_inventory_leds()

    def serial_port_init(self, port="/dev/ttyACM0", baudrate=38400, timeout=None):
        if self.serial_port and self.serial_port.is_open:
            print("Closing previous serial port...")
            self.serial_port.close()
        try:
            self.serial_port = serial.Serial(
                port=port, baudrate=baudrate, timeout=timeout
            )
            print(f"Serial port {port} opened successfully.")
        except serial.SerialException as e:
            print(f"Failed to open serial port: {e}")
            self.serial_port = None

    # Used in other pages to get App-scoped serial port
    def get_serial_port(self):
        return self.serial_port


class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Page One").pack(pady=10)
        tk.Button(
            self, text="Back to Idle", command=lambda: controller.show_frame("IdlePage")
        ).pack()


if __name__ == "__main__":
    app = App()
    app.mainloop()
