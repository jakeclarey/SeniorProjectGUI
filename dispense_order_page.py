# dispense_order_page.py
import tkinter as tk
from tkinter import ttk, messagebox

class DispenseOrderPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1024, height=600, bg="#0032A0")
        self.controller = controller

        # Track inventory and cart
        self.inventory_data = self.load_inventory()
        self.shopping_list = {}
        
        # Track total credits to be spent in order
        self.total_qty = 0
        
        # Track selected button and part
        self.selected_part = None
        self.selected_button = None
        
        # Part Button Frame (Populated in helper function: load_parts())
        self.parts_frame = tk.Frame(self, bg="#0032A0", width=350, height=450)
        self.parts_frame.place(x=10, y=150)
        
        # Shopping List Frame
        self.shopping_list_frame = tk.Frame(self, bg="white", width=350, height=365)
        self.shopping_list_frame.place(x=664, y=150)
        self.shopping_list_frame.pack_propagate(False)
        self.shopping_list_frame.grid_propagate(False)

        # Load in part selection buttons from Inventory.txt
        self.load_parts()
        
        # Title
        tk.Label(
            self,
            text="Select Hardware and Quantity",
            font=("Arial", 20),
            bg="#0032A0",
            fg="white",
        ).place(relx=0.5, y=100, anchor="center")
        
        # User info
        self.user_id_label = tk.Label(
            self, text="ID: -", font=("Arial", 16), fg="white", bg="#0032A0"
        )
        self.user_id_label.place(relx=1, y=10, anchor="ne", x=-10)

        self.credits_label = tk.Label(
            self, text="Credits: 0", font=("Arial", 16), fg="white", bg="#0032A0"
        )
        self.credits_label.place(relx=1, y=50, anchor="ne", x=-10)
        
        # Back button
        tk.Button(
            self,
            text="Back",
            font=("Arial", 14),
            width=12,
            height=2,
            bg="white",
            command=lambda: controller.show_frame("ActivityPage"),
        ).place(x=10, y=10)
        
        # View Available Stock button
        tk.Button(
            self,
            text="View Available Stock",
            font=("Arial", 14),
            width=20,
            height=2,
            bg="white",
            command=lambda: controller.show_frame("HardwareStockPage"),
        ).place(x=170, y=10)
        
        # Add to Order button
        tk.Button(
            self,
            text="Add to Order",
            font=("Arial", 14),
            width=12,
            height=2,
            bg="white",
            command=self.on_add_to_order,
        ).place(x=10, y=540)
        
        # Subtract from Order button
        tk.Button(
            self,
            text="Subtract from Order",
            font=("Arial", 14),
            width=20,
            height=2,
            bg="white",
            command=self.on_subtract_from_order,
        ).place(x=170, y=540)
        
        # Submit Order button
        tk.Button(
            self,
            text="Submit Order",
            font=("Arial", 14),
            width=20,
            height=2,
            bg="white",
            command=self.on_submit_order,
        ).place(x=1014, y=590, anchor="se")

        # Quantity slider
        self.quantity = tk.IntVar(value=5)

        self.slider = tk.Scale(
        self,
        from_=10,
        to=1,
        orient="vertical",
        variable=self.quantity,
        length=365,
        width=60,
        font=("Arial", 16),
        bg="#0032A0",
        fg="white",
        highlightthickness=0,
        troughcolor="white",
        )
        self.slider.place(x=370, y=150)

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
                            inventory[f"{category}:{name}"] = quantity
        except FileNotFoundError:
            inventory = {"No Data": 0}
        return inventory
        
    def parse_inventory_line(self, line):
        parts = line.strip().split(":")
        if len(parts) == 3:
            category = parts[0].strip()
            name = parts[1].strip()
            quantity = int(parts[2].strip())
            return f"{category}:{name}", quantity
        return None, None

    def load_parts(self):
        for widget in self.parts_frame.winfo_children():
            widget.destroy()

        try:
            with open("Inventory.txt", "r") as f:
                for line in f:
                    if line.strip():
                        part, qty = self.parse_inventory_line(line)
                        if part:
                            btn = tk.Button(
                                self.parts_frame,
                                text=f"{part}",
                                font=("Arial", 14),
                                width=30,
                                anchor="w",
                            )
                            btn.config(
                                command=lambda p=part, b=btn: self.select_part(p, b)
                            )
                            btn.pack(pady=3)
        except FileNotFoundError:
            pass

    def select_part(self, part, btn):
        # Reset previous selection
        if self.selected_button and self.selected_button != btn:
            self.selected_button.config(bg="#f0f0f0")  # Default light gray for buttons

        # Update new selection
        self.selected_part = part
        self.selected_button = btn
        btn.config(bg="yellow")
        
    def on_submit_order(self):
        if not self.shopping_list:
            messagebox.showwarning("Order is Empty", "Please make an order.")
            return
        self.credits -= self.total_qty
        self.update_keycard_file()
        self.update_hardware_list_txt()
        self.total_qty = 0
        self.selected_part = None
        self.selected_button = None
        self.update_inventory_txt()
        self.shopping_list.clear()
        self.after(0, lambda: self.controller.show_frame("DispensingPage"))
        
    def on_add_to_order(self):
        part = self.selected_part
        if not part:
            messagebox.showwarning("No Selection", "Please select a hardware item.")
            return
            
        qty = int(self.quantity.get())
        self.update_shopping_list(part, qty)
        self.update_shopping_list_frame()
        
    def on_subtract_from_order(self):
        part = self.selected_part
        if not part:
            messagebox.showwarning("No Selection", "Please select a hardware item.")
            return
            
        qty = int(self.quantity.get())
        self.update_shopping_list(part, -qty)
        self.update_shopping_list_frame()
        
    def update_shopping_list(self, part, qty):
        if (self.total_qty + qty) > self.credits:
            messagebox.showerror(
                    "Insufficient Credits", "You don't have enough credits."
                )
            return
        
        part = part.replace(":", " ")
        if part in self.shopping_list:
            max_qty = 50
            if (self.shopping_list[part] + qty) > max_qty:
                messagebox.showerror(
                    "Too Many Parts", f"The max order of a part type is {max_qty}."
                )
                return
            self.shopping_list[part] += qty
        else:
            self.shopping_list[part] = qty
        
        if self.shopping_list[part] <= 0:
                self.shopping_list.pop(part, None)
                
        self.total_qty += qty

        if self.total_qty < 0:
            self.total_qty = 0
        
    def update_inventory_txt(self):
        try:
            # Read all lines from Inventory.txt
            updated_lines = []
            with open("Inventory.txt", "r") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue

                    # Parse line
                    if ":" in line:
                        parts = line.split(":")
                        if len(parts) == 3:
                            category = parts[0].strip()
                            name = parts[1].strip()
                            quantity = int(parts[2].strip())

                            key = f"{category}:{name}"
                            # Check if this part is in the order
                            lookup_key = f"{category} {name}"  # shopping_list uses space instead of colon

                            if lookup_key in self.shopping_list:
                                ordered_qty = self.shopping_list[lookup_key]
                                quantity -= ordered_qty
                                if quantity < 0:
                                    quantity = 0

                            updated_line = f"{category}:{name}: {quantity}"
                            updated_lines.append(updated_line)
                        else:
                            updated_lines.append(line)
                    else:
                        updated_lines.append(line)

            with open("Inventory.txt", "w") as file:
                for line in updated_lines:
                    file.write(line + "\n")

        except Exception as e:
            print("Error updating inventory:", e)

        
    def update_hardware_list_txt(self):
        try:
            with open("hardware_list.txt", "w") as file:
                for part, qty in self.shopping_list.items():
                    file.write(";" + part + ":" + str(qty) + "\n")
        except Exception as e:
            print(f"Exception occured in update_hardware_list_txt: {e}")
            pass
        
    def update_shopping_list_frame(self):
        # Clear previous widgets
        for widget in self.shopping_list_frame.winfo_children():
            widget.destroy()

        row = 0
        for part, qty in self.shopping_list.items():
            label = tk.Label(
                self.shopping_list_frame,
                text=f"{part} x{qty}",
                font=("Arial", 14),
                anchor="w",
                bg="white"
            )
            label.grid(row=row, column=0, sticky="w", padx=10, pady=5)
            row += 1
        
        # Total credits used
        total_label = tk.Label(
            self.shopping_list_frame,
            text=f"Total Credits: {self.total_qty}",
            font=("Arial", 14, "bold"),
            bg="white",
            anchor="w",
            fg="#0032A0"
        )
        total_label.place(relx=0, rely=1, anchor="sw", x=10, y=-10)

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
        self.update_shopping_list_frame()
        self.controller.previous_page="DispenseOrderPage"
        super().tkraise(aboveThis)
