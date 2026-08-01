import time
import threading
from pynput.keyboard import Key, Controller as KeyboardController

keyboard = KeyboardController()

def send_mc_chat(message):
    """Sends a message directly into Minecraft in-game chat box"""
    def _send():
        try:
            time.sleep(0.15)
            keyboard.press('t')
            keyboard.release('t')
            time.sleep(0.2)

            for char in message:
                keyboard.press(char)
                keyboard.release(char)
                time.sleep(0.012)

            time.sleep(0.15)
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            time.sleep(0.15)
        except Exception as e:
            print(f"[Chat Error] {e}")

    threading.Thread(target=_send, daemon=True).start()
