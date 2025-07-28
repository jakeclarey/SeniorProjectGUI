# led_utils.py
from gpiozero import LED
import time

# Define red and yellow LEDs (use the same pins everywhere)
red_led = LED(24)
yellow_led = LED(23)


def update_inventory_leds(inventory_file="Inventory.txt"):
    print("Updating inventory LEDs")
    red_led.off()
    yellow_led.off()

    try:
        with open(inventory_file, "r") as f:
            for line in f:
                print(line)
                parts = line.strip().rsplit(": ", 1)
                if len(parts) == 2:
                    _, qty = parts
                    qty = int(qty)
                    if qty < 40:
                        red_led.on()
                        return
                    elif qty < 100:
                        yellow_led.on()
                        # don't return — keep looking for a possible red

        time.sleep(100)
    except FileNotFoundError:
        pass
