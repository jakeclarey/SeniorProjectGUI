# hardware_stock_page.py
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class HardwareStockPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1024, height=600, bg="#0032A0")
        self.controller = controller

        # Title
        title_label = tk.Label(self, text="Available Stock", font=("Arial", 28), fg="white", bg="#0032A0")
        title_label.pack(pady=20)

        # Back button
        back_button = tk.Button(self, text="Back", font=("Arial", 16), width=8, height=2,
                                command=lambda: controller.show_frame("HomePage"))
        back_button.place(x=10, y=10)

        # Load inventory and draw chart
        inventory = self.load_inventory()
        self.draw_bar_chart(inventory)

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

    def draw_bar_chart(self, inventory):
        
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame) or isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
                continue  # Keep static UI elements
            widget.destroy()
        
        # Create figure with white background
        fig, ax = plt.subplots(figsize=(9, 5), dpi=100)
        fig.patch.set_facecolor('white')
        
        # Data
        labels = list(inventory.keys())
        quantities = list(inventory.values())
        
        # Assign colors based on stock levels
        colors = []
        for qty in quantities:
            if qty < 40:
                colors.append("red")       # Critical low stock
            elif qty < 100:
                colors.append("yellow")    # Low stock warning
            else:
                colors.append("#4CAF50")   # Healthy stock (green)
        
        # Create vertical bar chart
        bars = ax.bar(labels, quantities, color=colors)
        
        # Add count labels inside each bar
        for bar, qty in zip(bars, quantities):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2,
            str(qty), ha='center', va='center', color='black' if qty < 100 else 'white',
            fontsize=12, fontweight='bold')
        
        # Set title and remove X-axis label
        ax.set_ylabel("Quantity", fontsize=14)
        ax.set_title("Hardware Inventory", fontsize=18)
        
        # Rotate x-axis labels for readability
        plt.xticks(rotation=45, ha='right')
        
        # Remove extra margins and fix cutoff
        plt.tight_layout()
        
        # Embed chart in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)
        

    def tkraise(self, aboveThis=None):
        inventory = self.load_inventory()
        self.draw_bar_chart(inventory)  # refresh chart each time this page is shown
        super().tkraise(aboveThis)
