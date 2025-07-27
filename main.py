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
from dispense_select_page import DispenseSelectPage
# from dispense_loading_page import DispenseLoadingPage
from PIL import Image, ImageTk

from led_utils import update_inventory_leds

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hardware Sorting System")
        #self.geometry("1024x600")
        self.attributes("-fullscreen", True)
        
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        
        self.current_user_id = None
        self.current_user_credits = None
        self.frames = {}
        
        for PageClass in (IdlePage, HomePage, HardwareStockPage, 
                        AdminPwdPage, AdminMenuPage, ActivityPage,
                        PreSortPage, SortHardwarePage, DispenseSelectPage, PageOne):
            page_name = PageClass.__name__
            frame = PageClass(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("IdlePage")
    
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        
        update_inventory_leds()

class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Page One").pack(pady=10)
        tk.Button(self, text="Back to Idle", command=lambda: controller.show_frame("IdlePage")).pack()


if __name__ == "__main__":
    app = App()
    app.mainloop()
