import pyautogui
import time

# 1. Give yourself a few seconds to switch to the target window
print("Starting in 3 seconds...")
time.sleep(5)

# 2. Mouse Actions
# Move to X=500, Y=500 over 1 second and click
pyautogui.moveTo(500, 500, duration=1)
pyautogui.click()

# Or click at a specific coordinate directly
# pyautogui.click(x=100, y=200)

# 3. Keyboard Actions
# Type a string with a small delay between each character
pyautogui.write("Hello, world!", interval=0.1)

# Press specific keys like 'enter' or 'esc'
pyautogui.press('enter')

# 4. Using Hotkeys (e.g., Ctrl+C or Alt+Tab)
pyautogui.hotkey('ctrl', 'a')  # Select all
