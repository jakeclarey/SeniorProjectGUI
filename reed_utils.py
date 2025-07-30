# reed_utils.py
from gpiozero import Button

# Pin assignment (change to match your wiring)
LID_SENSOR_PIN = 13  # GPIO13 (Pin 33 on Raspberry Pi)

# Set lid sensor as a button with an internal pull-up
lid_sensor = Button(LID_SENSOR_PIN, pull_up=True)


def check_lid_sensor():
    return lid_sensor.is_pressed
