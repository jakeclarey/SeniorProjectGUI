# dispense_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from dispensing_page import DispenseOrderPage
from led_utils import update_inventory_leds


class DispenseOrderPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1024, height=600, bg="#0032A0")
        self.controller = controller

        # Track inventory and cart
        self.inventory_data = self.load_inventory()
        self.shopping_list = []
        self.hardware_names = []

        # Top buttons
        tk.Button(
            self,
            text="Exit",
            font=("Arial", 14),
            width=12,
            height=2,
            bg="white",
            command=lambda: controller.show_frame("IdlePage"),
        ).place(x=10, y=10)
        tk.Button(
            self,
            text="View Available Stock",
            font=("Arial", 14),
            width=20,
            height=2,
            bg="white",
        ).place(x=170, y=10)

        # User info
        self.user_id_label = tk.Label(
            self, text="ID: -", font=("Arial", 16), fg="white", bg="#0032A0"
        )
        self.user_id_label.place(relx=1, y=10, anchor="ne", x=-10)

        self.credits_label = tk.Label(
            self, text="Credits: 0", font=("Arial", 16), fg="white", bg="#0032A0"
        )
        self.credits_label.place(relx=1, y=50, anchor="ne", x=-10)

        # Title
        tk.Label(
            self,
            text="Select Hardware and Quantity",
            font=("Arial", 20),
            bg="#0032A0",
            fg="white",
        ).place(relx=0.5, y=100, anchor="center")

        # Hardware buttons
        hardware_items = [
            "Screw: M2 x 10",
            "Screw: M3 x 8",
            "Screw: M3 x 16",
            "Screw: M3 x 30",
            "Screw: M3 x 50",
            "Nut: M2",
            "Nut: M3",
            "Locknut: M3",
            "Washer: M3",
        ]
        self.selected_hardware = tk.StringVar(value=None)

        btn_width = 14
        btn_height = 2
        x_padding = 25
        y_start_row1 = 140
        y_start_row2 = 200
        x_base_row1 = 140
        x_base_row2 = x_base_row1 + 75

        for i, item in enumerate(hardware_items):
            row = 0 if i < 5 else 1
            col = i if row == 0 else i - 5
            x_pos = (x_base_row1 if row == 0 else x_base_row2) + col * (
                btn_width * 9 + x_padding
            )
            y_pos = y_start_row1 if row == 0 else y_start_row2

            btn = tk.Radiobutton(
                self,
                text=item,
                indicatoron=0,
                width=btn_width,
                height=btn_height,
                font=("Arial", 12),
                bg="white",
                fg="black",
                variable=self.selected_hardware,
                value=item,
            )
            btn.place(x=x_pos, y=y_pos)

        # Quantity slider
        self.quantity = tk.IntVar(value=5)
        self.slider = ttk.Scale(
            self, from_=1, to=10, orient="horizontal", variable=self.quantity
        )
        self.slider.place(relx=0.5, y=340, width=700, anchor="center")

        self.slider_value_label = tk.Label(
            self,
            text=str(self.quantity.get()),
            font=("Arial", 14),
            bg="#0032A0",
            fg="white",
        )
        self.slider_value_label.place(relx=0.5, y=300, anchor="center")
        self.slider.bind(
            "<Motion>",
            lambda e: self.slider_value_label.config(
                text=str(int(self.quantity.get()))
            ),
        )

        # Finished button
        tk.Button(
            self,
            text="Finished",
            font=("Arial", 14),
            width=20,
            height=2,
            bg="white",
            command=self.on_finish,
        ).place(relx=0.5, y=450, anchor="center")

    def load_inventory(self):
        inventory = {}
        try:
            with open("Inventory.txt", "r") as file:
                for line in file:
                    if ":" in line:
                        parts = line.strip().split(":")
                        if len(parts) == 3:
                            category = parts[0].strip()
                            name = parts[1].strip()
                            quantity = int(parts[2].strip())
                            inventory[f"{category} {name}"] = quantity
        except FileNotFoundError:
            inventory = {"No Data": 0}
        return inventory

    def on_finish(self):
        part = self.selected_hardware.get()
        if not part:
            messagebox.showwarning("No Selection", "Please select a hardware item.")
            return

        qty = int(self.quantity.get())
        self.shopping_list.append((part, qty))
        self.hardware_names.append(part)
        self.show_shopping_list()

    def show_shopping_list(self):
        total_credits = sum(qty for _, qty in self.shopping_list)
        summary = "\n".join([f"{hw} x{qty}" for hw, qty in self.shopping_list])
        summary += f"\n\nTotal Credits: {total_credits}"

        result = messagebox.askyesnocancel(
            "Submit Order", f"{summary}\n\nSubmit this order?"
        )

        if result is None:
            return  # Cancel
        elif result is False:
            clear = messagebox.askyesno(
                "Clear Cart", "Clear shopping list and start over?"
            )
            if clear:
                self.shopping_list.clear()
                self.hardware_names.clear()
            return
        elif result is True:
            if total_credits > self.credits:
                messagebox.showerror(
                    "Insufficient Credits", "You don't have enough credits."
                )
                self.shopping_list.clear()
                self.hardware_names.clear()
                return

            for hw, qty in self.shopping_list:
                self.inventory_data[hw] -= qty

            self.credits -= total_credits
            self.controller.current_user_credits = self.credits
            self.credits_label.config(text=f"Credits: {self.credits}")

            with open("hardware_list.txt", "w") as f:
                entries = [
                    f"{hw.replace(':', '')}:{qty}" for hw, qty in self.shopping_list
                ]
                f.write(";".join(entries))

            with open("Inventory.txt", "w") as f:
                for hw, qty in self.inventory_data.items():
                    f.write(f"{hw}: {qty}\n")

            self.update_keycard_file()
            DISPENSE_LOADING_SCREEN()
            self.shopping_list.clear()
            self.hardware_names.clear()

    def update_keycard_file(self):
        with open("Keycard_Scan_Entries.txt", "r") as f:
            lines = f.readlines()

        with open("Keycard_Scan_Entries.txt", "w") as f:
            for line in lines:
                if f"User ID: {self.user_id}" in line:
                    parts = line.strip().split(",")
                    for i in range(len(parts)):
                        if "Credits" in parts[i]:
                            parts[i] = f" Credits: {self.credits}"
                    line = ",".join(parts) + "\n"
                f.write(line)

    def set_user_info(self, user_id, credits):
        self.user_id = user_id
        self.credits = credits
        self.user_id_label.config(text=f"ID: {user_id}")
        self.credits_label.config(text=f"Credits: {credits}")

    def tkraise(self, aboveThis=None):
        self.set_user_info(
            self.controller.current_user_id, self.controller.current_user_credits
        )
        super().tkraise(aboveThis)
