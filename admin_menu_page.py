# admin_menu_page.py
import tkinter as tk
from tkinter import messagebox


class AdminMenuPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1024, height=600, bg="#0032A0")
        self.controller = controller

        self.selected_part = None
        self.selected_button = None
        self.entry_value = tk.StringVar(value="")

        # Title
        tk.Label(self, text="Admin Menu", font=("Arial", 24), fg="white", bg="#0032A0")\
            .place(relx=0.5, y=40, anchor="center")

        # Left: Part List Frame
        self.parts_frame = tk.Frame(self, bg="#0032A0", width=350, height=450)
        self.parts_frame.place(x=20, y=100)

        self.load_parts()

        # Right: Numpad + Controls Frame
        control_frame = tk.Frame(self, bg="#0032A0")
        control_frame.place(relx=0.65, rely=0.5, anchor="center")

        # Selected Part Label
        self.selected_label = tk.Label(control_frame, text="Selected: None",
                                       font=("Arial", 16), fg="white", bg="#0032A0")
        self.selected_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # Entry Display
        self.entry_display = tk.Entry(control_frame, textvariable=self.entry_value,
                                      font=("Arial", 18), justify="center", width=10)
        self.entry_display.grid(row=1, column=0, columnspan=3, pady=(0, 10))

        # Numpad Buttons
        buttons = [
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2),
            ('7', 4, 0), ('8', 4, 1), ('9', 4, 2),
            ('0', 5, 1), ('CLR', 5, 0), ('OK', 5, 2)
        ]
        for (text, r, c) in buttons:
            tk.Button(control_frame, text=text, font=("Arial", 18), width=5, height=2,
                      command=lambda t=text: self.numpad_press(t)).grid(row=r, column=c, padx=5, pady=5)

        # + and - Buttons
        tk.Button(control_frame, text="+", font=("Arial", 18), width=5, height=2,
                  command=lambda: self.adjust_stock("inc")).grid(row=6, column=0, pady=(10, 0))
        tk.Button(control_frame, text="-", font=("Arial", 18), width=5, height=2,
                  command=lambda: self.adjust_stock("dec")).grid(row=6, column=1, pady=(10, 0))

        # Bottom-right control buttons
        tk.Button(self, text="Reset All Stock to 200", font=("Arial", 14),
                  command=self.reset_all_stock).place(relx=1, rely=1, anchor="se", x=-20, y=-20)
        tk.Button(self, text="Clear Keycard Entries", font=("Arial", 14),
                  command=self.clear_keycard_entries).place(relx=1, rely=1, anchor="se", x=-20, y=-70)
        tk.Button(self, text="Set Selected to 0", font=("Arial", 14),
                  command=lambda: self.adjust_stock("zero")).place(relx=1, rely=1, anchor="se", x=-20, y=-120)

        # Back button
        tk.Button(self, text="Back", font=("Arial", 14), width=8, height=2,
                  command=lambda: controller.show_frame("HomePage")).place(x=10, y=10)

    # ------------------------
    # Inventory Handling
    # ------------------------
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
                            btn = tk.Button(self.parts_frame, text=f"{part}: {qty}", font=("Arial", 14),
                                            width=30, anchor="w")
                            btn.config(command=lambda p=part, b=btn: self.select_part(p, b))
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
        self.selected_label.config(text=f"Selected: {part}")


    def get_current_stock(self, part):
        try:
            with open("Inventory.txt", "r") as f:
                for line in f:
                    p, qty = self.parse_inventory_line(line)
                    if p == part:
                        return qty
        except FileNotFoundError:
            return 0
        return 0

    # ------------------------
    # Stock Modification Logic
    # ------------------------
    def adjust_stock(self, mode="set"):
        if not self.selected_part:
            messagebox.showerror("Error", "Select a part first!")
            return

        if mode != "zero" and not self.entry_value.get().isdigit():
            messagebox.showerror("Error", "Enter a valid number!")
            return

        current = self.get_current_stock(self.selected_part)
        if mode == "set":
            new_stock = int(self.entry_value.get())
        elif mode == "inc":
            new_stock = current + int(self.entry_value.get())
        elif mode == "dec":
            new_stock = max(0, current - int(self.entry_value.get()))
        elif mode == "zero":
            new_stock = 0

        self.modify_stock(self.selected_part, new_stock)
        self.entry_value.set("")
        self.load_parts()
        self.selected_button = None
        self.selected_part = None
        self.selected_label.config(text="Selected: None")


    def modify_stock(self, part, new_stock):
        try:
            lines = []
            with open("Inventory.txt", "r") as f:
                for line in f:
                    p, qty = self.parse_inventory_line(line)
                    if p == part:
                        lines.append(f"{p}:{new_stock}\n")
                    else:
                        lines.append(line)
            with open("Inventory.txt", "w") as f:
                f.writelines(lines)
        except FileNotFoundError:
            pass

    # ------------------------
    # Other Admin Actions
    # ------------------------
    def reset_all_stock(self):
        try:
            lines = []
            with open("Inventory.txt", "r") as f:
                for line in f:
                    p, _ = self.parse_inventory_line(line)
                    if p:
                        lines.append(f"{p}:200\n")
            with open("Inventory.txt", "w") as f:
                f.writelines(lines)
            messagebox.showinfo("Success", "All stock reset to 200")
            self.load_parts()
        except FileNotFoundError:
            pass

    def clear_keycard_entries(self):
        with open("Keycard_Scan_Entries.txt", "w") as f:
            f.write("\n")
        messagebox.showinfo("Success", "Keycard entries cleared")

    def numpad_press(self, key):
        if key == "CLR":
            self.entry_value.set("")
        elif key == "OK":
            self.adjust_stock("set")
        else:
            self.entry_value.set(self.entry_value.get() + key)
