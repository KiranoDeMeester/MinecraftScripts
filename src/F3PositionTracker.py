import re
import time
import pyperclip
from src.DirectInput import trigger_f3_c

def get_minecraft_position():
    """Triggers F3+C and parses current player coordinates (x, y, z, yaw, pitch)"""
    trigger_f3_c()
    time.sleep(0.15)
    text = pyperclip.paste()
    
    match = re.search(r'(?:tp|teleport)\s+@s\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)', text)
    if match:
        return {
            'x': float(match.group(1)),
            'y': float(match.group(2)),
            'z': float(match.group(3)),
            'yaw': float(match.group(4)),
            'pitch': float(match.group(5))
        }
    return None
