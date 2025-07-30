# sort_hardware_page.py
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading
import time
from ultralytics import YOLO
import math


class SortHardwarePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1024, height=600, bg="#0032A0")
        self.controller = controller
        self.inventory = self.load_inventory()

        # User info (top-right)
        self.user_id_label = tk.Label(
            self, text="ID: -", font=("Arial", 16), fg="white", bg="#0032A0"
        )
        self.user_id_label.place(relx=1, y=10, anchor="ne", x=-10)

        self.credits_label = tk.Label(
            self, text="Credits: 0", font=("Arial", 16), fg="white", bg="#0032A0"
        )
        self.credits_label.place(relx=1, y=50, anchor="ne", x=-10)

        # Status message (bottom center)
        self.status_label = tk.Label(
            self, text="Initializing...", font=("Arial", 16), fg="white", bg="#0032A0"
        )
        self.status_label.place(relx=0.5, rely=0.95, anchor="center")

        # Frame for live feed
        self.feed_frame = tk.Frame(
            self, bg="white", highlightbackground="black", highlightthickness=25
        )
        self.feed_frame.place(
            relx=0.5, rely=0.5, anchor="center", width=600, height=400
        )

        self.video_label = tk.Label(self.feed_frame, bg="white")
        self.video_label.pack(expand=True)

        # Internal state
        self.running = False
        self.last_detection_time = None
        self.sorting_thread = None
        self.ser = self.controller.get_serial_port()
        self.cap = None
        self.model = None
        self.current_part_class = None
        self.session_credits = 0
        self.input_size = 640  # YOLOv8 default input size

        # Class names in order from YOLO model
        self.class_names = [
            "M2x0.4-10mm",
            "M2x0.4-LSNUT",
            "M3x0.5-16mm",
            "M3x0.5-30mm",
            "M3x0.5-50mm",
            "M3x0.5-8mm",
            "M3x0.5-FW",
            "M3x0.5-LSNUT",
            "M3x0.5-MSLNUT",
        ]

        # Names to send over UART for sort ramp control
        self.stepper_names = [
            "Screw M2 x 10",
            "Nut M2",
            "Screw M3 x 16",
            "Screw M3 x 30",
            "Screw M3 x 50",
            "Screw M3 x 8",
            "Washer M3",
            "Nut M3",
            "Locknut M3",
        ]

        # Mapping YOLO class names to inventory names
        self.class_name_mapping = {
            "M2x0.4-10mm": "Screw:M2 x 10",
            "M2x0.4-LSNUT": "Nut:M2",
            "M3x0.5-16mm": "Screw:M3 x 16",
            "M3x0.5-30mm": "Screw:M3 x 30",
            "M3x0.5-50mm": "Screw:M3 x 50",
            "M3x0.5-8mm": "Screw:M3 x 8",
            "M3x0.5-FW": "Washer:M3",
            "M3x0.5-LSNUT": "Nut:M3",
            "M3x0.5-MSLNUT": "Locknut:M3",
        }

    def set_user_info(self, user_id, credits):
        self.user_id_label.config(text=f"ID: {user_id}")
        self.credits_label.config(text=f"Credits: {credits}")

    def tkraise(self, aboveThis=None):
        self.session_credits = 0
        self.set_user_info(
            self.controller.current_user_id, self.controller.current_user_credits
        )
        self.inventory = self.load_inventory()

        super().tkraise(aboveThis)

        self.status_label.config(text="Starting sorting process...")
        self.running = True
        self.sorting_thread = threading.Thread(
            target=self.run_sorting_process, daemon=True
        )
        self.sorting_thread.start()
        self.check_sorting_finished()

    def check_sorting_finished(self):
        if not self.running:
            self.status_label.config(text=f"You earned {self.session_credits} credits!")
            self.after(3000, lambda: self.controller.show_frame("ActivityPage"))
        else:
            self.after(500, self.check_sorting_finished)  # Keep checking every 500ms

    def run_sorting_process(self):
        try:
            # Load YOLOv8 ONNX model
            self.status_label.config(text="Loading model...")
            model_path = "newbest.onnx"
            self.model = YOLO(model_path, task="detect")

            # Open camera
            self.status_label.config(text="Opening camera...")
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.status_label.config(text="Camera not found")
                time.sleep(3)
                return
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            # Open serial port
            # Waiting a short moment to ensure serial port is closed from last use
            time.sleep(1)
            self.status_label.config(text="Connecting to motor controller...")

            # Start sort command
            self.send_command("sort_start\n")

            # Send motors_on
            self.send_command("motors_on\n")

            self.status_label.config(text="Sorting in progress...")
            self.last_detection_time = time.time()
            timeout_interval = 20

            while self.running:

                # If no parts detected for x seconds, exit sort flow
                if (time.time() - self.last_detection_time) > timeout_interval:
                    self.status_label.config(text="Timeout: No parts detected")
                    break

                self.status_label.config(
                    text=f"Time elapsed since last detection... {int(time.time() - self.last_detection_time)}"
                )
                ret, frame = self.cap.read()
                if not ret:
                    self.current_part = None
                    continue

                results = self.model(frame, verbose=False)
                annotated_frame = results[0].plot()
                self.update_feed(annotated_frame)

                detected = False
                if len(results[0].boxes) == 0:
                    self.current_part = None
                    continue
                else:
                    detected = True

                if detected:
                    self.last_detection_time = time.time()
                    # Stop motors
                    self.send_command("motors_off\n")
                    time.sleep(0.5)  # Wait for parts to stop

                    # Re-check with another frame
                    ret, frame = None, None
                    ret, frame = self.cap.read()
                    if ret:
                        results = self.model(frame, verbose=False)
                    else:
                        self.send_command("motors_on\n")
                        continue

                    # Find object closest to ramp (max x2)
                    closest_idx = None
                    max_x2 = -float("inf")
                    for i, box in enumerate(results[0].boxes):
                        x2 = box.xyxy[0][2].item()
                        if x2 > max_x2:
                            max_x2 = x2
                            closest_idx = i

                # If object is too far right (beyond frame), restart motors
                if max_x2 >= 640:
                    self.send_command("motors_on\n")
                    continue

                if closest_idx is None:
                    # Resume motors and continue
                    self.send_command("motors_on\n")
                    continue

                # Get confidence and class
                confidence = math.ceil((results[0].boxes[closest_idx].conf * 100)) / 100
                self.current_part_class = int(results[0].boxes.cls[closest_idx])

                if confidence > 0.90:
                    self.status_label.config(
                        text=f"Now sorting {self.class_names[self.current_part_class]}"
                    )

                    # Calculate steps to drop part
                    x1, y1, x2, y2 = results[0].boxes.xyxy[closest_idx]
                    center_x = int((x2 + x1) / 2)
                    # length_x = int(x2 - x1)

                    # [WARNING] THIS DOES NOT WORK DUE TO THE CAMERA NOT BEING PARALLEL TO THE CONVEYOR
                    # steps_per_inch_belt_travel = 3200 / 0.96 (determined by datasheets and CAD models)
                    #

                    # Frame is 640 pixels and there are 6.33 inches of conveyor in frame
                    # ~3200 steps are required to fully push a part off the full conveyor (7.83 inches start to end)
                    # pixels_per_inch = 640 / 6.33
                    # steps_per_inch = 3200 / 7.83
                    # steps_per_pixel = steps_per_inch / pixels_per_inch
                    # pixels_per_inch = 101.106  # pre-calculated
                    # steps_per_pixel = 4.042  # pre-calculated

                    # TODO LINEAR REGRESSION MAPPING. MAP PIXELS-STEPS IN TUPLE FOR SET STEP WIDTHS
                    # USE INTERPOLATION BETWEEN THEM TO DETERMINE APPROPRIATE PIXELS-STEPS CURVE FUNCTION

                    # Number of steps to get right edge of the part to the end of the conveyor
                    # num_steps = int(
                    #     (640 - x2) * steps_per_pixel + 1.5 * pixels_per_inch
                    # )

                    # depth = (-6.2e-6) * (x2 ** 2) + 0.014 * x2  # depth in inches from start of visible belt
                    # distance_to_push = 6.33 - depth             # distance left to reach end of belt
                    # num_steps = int(distance_to_push * 3333.33) # convert inches to motor steps

                    # num_steps = 0.01209307 * (x2 ** 2) + 20.08856 * x2 + 5000
                    num_steps = self.get_steps_from_x2(x2)

                    # num_steps = int(640 - (center_x + 0.2 * length_x)) * alpha

                    # Draw detections on frame
                    annotated_frame = results[0].plot()
                    self.update_feed(annotated_frame)

                    # Send stepper command string
                    command_string = (
                        f"{self.stepper_names[self.current_part_class]}:{num_steps}\n"
                    )

                    self.send_command(command_string)

                    self.status_label.config(
                        text=f"Sorted: {self.class_names[self.current_part_class]}"
                    )
                    self.session_credits += 1
                    print("Attempting to increment stock")
                    self.increment_stock(
                        self.class_name_mapping[
                            self.class_names[self.current_part_class]
                        ],
                        1,
                    )
                    self.increment_user_credits()
                    self.update_ui_credits()

                    # Resume motors
                    self.send_command("motors_on\n")
                else:
                    command_string = "trash\n"
                    command_string.encode()
                    self.send_command(command_string)
                time.sleep(1)

            self.cleanup()

        except Exception as e:
            self.status_label.config(text=f"Error: {e}")
            print("Exception in sorting thread:", e)
            time.sleep(3)
            self.cleanup()

    def send_command(self, command):
        print(f"Sending {command}")
        self.ser.write(command.encode())
        while True:
            response = self.ser.readline().decode()
            print(response)
            if response == "ACK\n":
                break

    def update_feed(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = img.resize((600, 400))
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)

    def increment_user_credits(self):
        self.controller.current_user_credits += 1
        file_path = "Keycard_Scan_Entries.txt"
        with open(file_path, "r") as f:
            lines = f.readlines()
        with open(file_path, "w") as f:
            f.write("\n")  # Keep leading newline
            for line in lines[1:]:
                if f"User ID: {self.controller.current_user_id}" in line:
                    parts = line.strip().split(", ")
                    credits = int(parts[1].split(": ")[1]) + 1
                    f.write(
                        f"User ID: {self.controller.current_user_id}, Credits: {credits}\n"
                    )
                else:
                    f.write(line)

    def update_ui_credits(self):
        self.credits_label.config(
            text=f"Credits: {self.controller.current_user_credits}"
        )

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

    def get_steps_from_x2(self, x2):
        calibration_data = [
            (100, 4560),  # Working
            (200, 4460),  # Working
            (280, 4000),  # Added in upon observation
            (300, 3800),  # Was 4066 and .25 seconds too long
            (320, 3650),  # Working
            (340, 3500),  # Working
            (380, 3030),  # Working
            (400, 2560),  # Was 2666 and part hanging off
            (420, 2960),  # Working
            (460, 3000),  # Working
            (500, 3200),  # Working ?
            (600, 2000),  # Was 1900 and 0.1 seconds too short
            (640, 1200),  # Have never seen, also will not occur as at 640 it trashes
        ]

        for i in range(len(calibration_data) - 1):
            x_low, steps_low = calibration_data[i]
            x_high, steps_high = calibration_data[i + 1]

            if x_low <= x2 <= x_high:
                ratio = (x2 - x_low) / (x_high - x_low)
                interpolated_steps = steps_low + ratio * (steps_high - steps_low)
                return int(interpolated_steps)

        # If x2 is outside the known range, return the closest known value
        if x2 < calibration_data[0][0]:
            return calibration_data[0][1]
        else:
            return calibration_data[-1][1]

    def increment_stock(self, part, stock_increment):
        print(f"Inventory dict: {self.inventory}")
        try:
            if part in self.inventory:
                self.inventory[part] += stock_increment
            else:
                self.inventory[part] = 0
            print(f"Updated inventory dict: {self.inventory}")
        except Exception as e:
            print(f"Exception occurred: {e}")
            pass

    def update_inventory(self, inventory):
        print("Updating Inventory")
        try:
            with open("Inventory.txt", "w") as file:
                print("Inventory.txt opened in write mode")
                for key, pair in inventory.items():
                    print(f"Writing to inventory file: {key}:{pair}")
                    file.write(f"{key}:{pair}\n")
        except FileNotFoundError:
            print("[ERROR]: Inventory.txt not found after sorting process.")

    def cleanup(self):
        self.running = False
        if self.cap:
            self.cap.release()
        if self.ser:
            try:
                self.send_command("motors_off\n")
                time.sleep(1)
                self.update_inventory(self.inventory)
                time.sleep(1)
                self.send_command("sorting_done\n")
                time.sleep(1)
                self.ser.flush()
            except:
                pass
