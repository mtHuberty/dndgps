import pyautogui

from PIL import ImageGrab
from functools import partial

ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

def capture_screenshot():
    try:
        # Capture the screenshot
        screenshot = pyautogui.screenshot()

        # Crop to the minimap
        x = 2550 - 327
        y = 1440 - 336
        length = 290        
        cropped_screenshot = screenshot.crop((x, y, x + length, y + length))

        # Save the screenshot
        cropped_screenshot.save("sample.png")
    except Exception as e:
        print("Error:", e)

capture_screenshot()
