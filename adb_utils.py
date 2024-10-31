import subprocess
import cv2
import os

def connect_to_emulator(emulator_name):
    subprocess.run(["adb", "connect", emulator_name])

def take_screenshot():
    screenshot_path = os.path.join("images", "screenshot.png")
    subprocess.run(["adb", "shell", "screencap", "/sdcard/screenshot.png"])
    subprocess.run(["adb", "pull", "/sdcard/screenshot.png", screenshot_path])
    return cv2.imread(screenshot_path)

def click_position(x, y):
    subprocess.run(['adb', 'shell', 'input', 'tap', str(x), str(y)])

def find_subimage(screenshot, subimage):
    result = cv2.matchTemplate(screenshot, subimage, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    return max_loc, max_val
