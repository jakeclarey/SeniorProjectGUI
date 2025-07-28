# led_utils.py
from gpiozero import LED

# Define red and yellow LEDs (use the same pins everywhere)
red_led = LED(24)
yellow_led = LED(23)


def update_inventory_leds(inventory_file="Inventory.txt"):
    red_led.off()
    yellow_led.off()

    try:
        with open(inventory_file, "r") as f:
            for line in f:
                qty = int(line.strip().rsplit(":", 1)[-1])
                if qty < 40:
                    red_led.on()
                    return
                elif qty < 100:
                    yellow_led.on()
                    # don't return — keep looking for a possible red
    except FileNotFoundError:
        pass
