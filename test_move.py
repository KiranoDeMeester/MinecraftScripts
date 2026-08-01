import time
from src.DirectInput import press_key, release_key, KEY_W, click_mouse_left

print("==================================================")
print("     DIRECT HARDWARE KEYBOARD & MOUSE TEST        ")
print("==================================================")
print("Switch to your Minecraft window NOW!")
print("Starting countdown...")
for i in range(3, 0, -1):
    print(f"  {i}...")
    time.sleep(1)

print("\n>>> HOLDING W KEY FOR 3 SECONDS... <<<")
press_key(KEY_W)
time.sleep(3.0)
release_key(KEY_W)

print(">>> CLICKING LEFT MOUSE (MINING)... <<<")
click_mouse_left(1.5)

print("\n[TEST FINISHED] Did your player move or mine?")
