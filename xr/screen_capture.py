import pyautogui
import os
from datetime import datetime
import pygetwindow as gw
import time
import numpy as np

# NOTE (Gabe): This ONLY works for windows os

filename_table = {
    # FILE_NAME: FILE PATH
}

def window_screenshot(window_title="", save_folder=""):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    file_path = os.path.join(save_folder, filename)

    if window_title == "":
        # Take screenshot of the full screen
        screenshot = pyautogui.screenshot()
        screenshot.save(file_path)

        filename_table[filename] = file_path
        return {
            'filename': filename,
        }

    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print(f"No windows found with title: {window_title}")
        return None

    window = windows[0]
    print(f"Found window: {window.title}")

    # Try to activate window, if fails use minimize/maximize/restore workaround
    try:
        window.activate()
        print("Window activated normally")
    except Exception as e:
        print("Normal activation failed, trying workaround...")
        window.minimize()
        time.sleep(0.2)
        window.maximize()
        time.sleep(0.2)
        window.restore()
        time.sleep(0.2)
        print("Workaround completed")

    # Take screenshot of the window
    screenshot = None
    try:
        screenshot = pyautogui.screenshot(region=(
            window.left,
            window.top,
            window.width,
            window.height
        ))
        print(f"Screenshot captured: {screenshot.size}")
        screenshot.save(file_path)
    except Exception as capture_error:
        print(f"Error capturing window: {capture_error}")
        print("Falling back to full screen capture")
        screenshot = pyautogui.screenshot()
        # Save the screenshot
        screenshot.save(file_path)

    filename_table[filename] = file_path
    return {
        'filename': filename,
    }
