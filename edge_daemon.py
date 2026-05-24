import time
import threading
import json
import sys
import os
from evdev import InputDevice, ecodes
import pyautogui

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

try:
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
except FileNotFoundError:
    print("Error: config.json not found. Please run panner_gui.py first.")
    sys.exit(1)

DEVICE_PATH = config["device_path"]
X_MAX = config["x_max"]
Y_MAX = config["y_max"]
EDGE_TOLERANCE = config["edge_tolerance"]
PAN_SPEED = config["pan_speed"]

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

state = {'x': 2000, 'y': 1000, 'touching': False}

print(f"Daemon active on {DEVICE_PATH}. Press Ctrl+C to stop.")

def read_events():
    device = InputDevice(DEVICE_PATH)
    for event in device.read_loop():
        if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
            state['touching'] = (event.value == 1)
        elif event.type == ecodes.EV_ABS:
            if event.code == ecodes.ABS_X:
                state['x'] = event.value
            elif event.code == ecodes.ABS_Y:
                state['y'] = event.value

reader_thread = threading.Thread(target=read_events, daemon=True)
reader_thread.start()

try:
    while True:
        if state['touching']:
            move_x, move_y = 0, 0

            if state['x'] > (X_MAX - EDGE_TOLERANCE): move_x = PAN_SPEED
            elif state['x'] < EDGE_TOLERANCE: move_x = -PAN_SPEED

            if state['y'] > (Y_MAX - EDGE_TOLERANCE): move_y = PAN_SPEED
            elif state['y'] < EDGE_TOLERANCE: move_y = -PAN_SPEED

            if move_x != 0 or move_y != 0:
                pyautogui.move(move_x, move_y)

        time.sleep(0.005)

except KeyboardInterrupt:
    print("\nExiting...")
