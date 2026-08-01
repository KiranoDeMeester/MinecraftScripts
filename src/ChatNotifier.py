import time
import threading
import pyperclip
from src.DirectInput import press_key, release_key, KEY_T, KEY_ENTER

# DirectInput scan codes for Ctrl (0x1D) and V (0x2F)
KEY_CTRL = 0x1D
KEY_V = 0x2F

def send_mc_chat(message):
    """Sends a message into Minecraft chat box instantly via Clipboard Paste (Ctrl+V) to prevent letter stuttering"""
    def _send():
        try:
            pyperclip.copy(message)
            time.sleep(0.1)

            # Open chat with T
            press_key(KEY_T)
            time.sleep(0.05)
            release_key(KEY_T)
            time.sleep(0.2)

            # Paste message with Ctrl + V
            press_key(KEY_CTRL)
            press_key(KEY_V)
            time.sleep(0.05)
            release_key(KEY_V)
            release_key(KEY_CTRL)
            time.sleep(0.15)

            # Press Enter
            press_key(KEY_ENTER)
            time.sleep(0.05)
            release_key(KEY_ENTER)
            time.sleep(0.1)
        except Exception as e:
            print(f"[Chat Error] {e}")

    threading.Thread(target=_send, daemon=True).start()
