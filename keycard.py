# keycard_scan.py
from gpiozero import Button
import time

# Define GPIO pins for Wiegand D0 and D1
D0 = Button(17)
D1 = Button(27)

rfid_bits = ""
last_read_time = time.time()

current_user_id = None


# Callback handlers
def d0_callback():
    global rfid_bits, last_read_time
    rfid_bits += "0"
    last_read_time = time.time()


def d1_callback():
    global rfid_bits, last_read_time
    rfid_bits += "1"
    last_read_time = time.time()


# Attach callbacks initially
D0.when_pressed = d0_callback
D1.when_pressed = d1_callback


def scan():
    global current_user_id, rfid_bits

    while True:
        rfid_bits = ""
        last_read_time = time.time()

        # Temporarily disable callbacks to flush any noise
        D0.when_pressed = None
        D1.when_pressed = None
        time.sleep(0.1)

        # Re-enable callbacks cleanly
        D0.when_pressed = d0_callback
        D1.when_pressed = d1_callback

        # Wait for either full 26-bit card or timeout
        while time.time() - last_read_time < 4:
            time.sleep(0.01)
            if len(rfid_bits) == 26:
                student_id_decimal = int(rfid_bits, 2)
                store_student_id(student_id_decimal)
                current_user_id = student_id_decimal
                return student_id_decimal

        # Clear bits if timeout
        rfid_bits = ""
        time.sleep(0.1)
        return None


def store_student_id(student_id_decimal):
    try:
        with open("Keycard_Scan_Entries.txt", "r") as file:
            entries = file.readlines()
    except FileNotFoundError:
        entries = []

    for line in entries:
        if f"User ID: {student_id_decimal}" in line:
            return

    with open("Keycard_Scan_Entries.txt", "a") as file:
        file.write(f"User ID: {student_id_decimal}, Credits: 100\n")


def get_user_credits(student_id):
    student_id_decimal = (
        int(student_id)
        if isinstance(student_id, str) and student_id.isdigit()
        else student_id
    )

    try:
        with open("Keycard_Scan_Entries.txt", "r") as file:
            for line in file:
                if f"User ID: {student_id_decimal}" in line:
                    parts = line.strip().split(",")
                    for part in parts:
                        if "Credits" in part:
                            return int(part.strip().split(":")[1])
    except FileNotFoundError:
        return 0

    return 0
