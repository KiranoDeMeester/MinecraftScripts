"""
===================================================================
CUSTOM BARITONE AI BOT - IN-GAME CHAT NOTIFIER (MINECRAFT 26.2)
===================================================================
Features:
- Types Baritone status messages DIRECTLY into your in-game Minecraft chat box!
- #clear <minX> <minY> <minZ> <maxX> <maxY> <maxZ>
- #goto <x> <z>
- #mine <block_name>
- #stop

Hotkeys:
  [F8] -> Start / Pause execution
  [F9] -> Emergency Stop & Exit
"""

import time
import threading
import sys
from pynput.keyboard import Key, Controller as KeyboardController, Listener as KeyboardListener
from pynput.mouse import Button, Controller as MouseController

keyboard = KeyboardController()
mouse = MouseController()

# Global State
active = False
running = True
current_task = None
task_params = {}

def send_mc_chat(text):
    """Types a message directly into the Minecraft in-game chat box"""
    try:
        time.sleep(0.2)
        keyboard.press('t')
        keyboard.release('t')
        time.sleep(0.25)

        for char in text:
            keyboard.press(char)
            keyboard.release(char)
            time.sleep(0.015)

        time.sleep(0.15)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(0.2)
    except Exception as e:
        print(f"[CHAT ERROR] {e}")

def log(msg, send_to_game=True):
    print(f"[BARITONE] {msg}", flush=True)
    if send_to_game:
        # Send in a separate thread so it doesn't block worker loops
        threading.Thread(target=send_mc_chat, args=(f"[Baritone] {msg}",), daemon=True).start()

def on_press(key):
    global active, running
    try:
        if key == Key.f8:
            active = not active
            if active:
                log("Bot STARTED! Press F8 to pause.", send_to_game=True)
            else:
                log("Bot PAUSED. Press F8 to resume.", send_to_game=True)
        elif key == Key.f9:
            log("EMERGENCY STOP ACTIVATED!", send_to_game=True)
            active = False
            running = False
            sys.exit(0)
    except Exception:
        pass

def eat_food():
    log("Eating bread from Hotbar Slot 1...", send_to_game=True)
    keyboard.press('1')
    keyboard.release('1')
    time.sleep(0.2)
    
    mouse.press(Button.right)
    time.sleep(3.2)
    mouse.release(Button.right)
    time.sleep(0.2)
    
    keyboard.press('2') # Return to pickaxe
    keyboard.release('2')

def equip_tool(tool_type):
    if tool_type == 'pickaxe':
        keyboard.press('2')
        keyboard.release('2')
    elif tool_type == 'shovel':
        keyboard.press('3')
        keyboard.release('3')
    time.sleep(0.1)

def execute_clear_task(params):
    minX, minY, minZ = params['minX'], params['minY'], params['minZ']
    maxX, maxY, maxZ = params['maxX'], params['maxY'], params['maxZ']

    total_blocks = (abs(maxX - minX) + 1) * (abs(maxY - minY) + 1) * (abs(maxZ - minZ) + 1)
    mined_blocks = 0
    eat_timer = time.time()

    log(f"Excavating area ({minX},{minY},{minZ}) to ({maxX},{maxY},{maxZ})", send_to_game=True)

    for y in range(maxY, minY - 1, -1):
        if not active or not running: return
        log(f"Mining Layer Y = {y}", send_to_game=False)
        
        for x in range(minX, maxX + 1):
            for z in range(minZ, maxZ + 1):
                if not active or not running: return

                if time.time() - eat_timer > 60:
                    eat_food()
                    eat_timer = time.time()

                if y > 132:
                    equip_tool('shovel')
                else:
                    equip_tool('pickaxe')

                mouse.press(Button.left)
                for _ in range(3):
                    if not active: break
                    mouse.move(15, 0)
                    time.sleep(0.2)
                for _ in range(6):
                    if not active: break
                    mouse.move(-15, 0)
                    time.sleep(0.2)
                for _ in range(3):
                    if not active: break
                    mouse.move(15, 0)
                    time.sleep(0.2)
                mouse.release(Button.left)

                keyboard.press('w')
                time.sleep(0.25)
                keyboard.release('w')

                mined_blocks += 1
                progress = int((mined_blocks / total_blocks) * 100)
                if mined_blocks % 20 == 0:
                    log(f"Progress: {progress}% complete ({mined_blocks}/{total_blocks})", send_to_game=True)

    log("🎉 #clear task 100% complete!", send_to_game=True)

def execute_goto_task(params):
    targetX, targetZ = params['targetX'], params['targetZ']
    log(f"Walking to coordinates ({targetX}, {targetZ})...", send_to_game=True)
    
    keyboard.press('w')
    while active and running:
        mouse.press(Button.left)
        time.sleep(0.4)
        mouse.release(Button.left)
        time.sleep(0.2)
    keyboard.release('w')

def bot_worker():
    global active, current_task, task_params
    while running:
        if active and current_task:
            if current_task == 'clear':
                execute_clear_task(task_params)
                current_task = None
                active = False
            elif current_task == 'goto':
                execute_goto_task(task_params)
                current_task = None
                active = False
            elif current_task == 'mine':
                equip_tool('pickaxe')
                mouse.press(Button.left)
                time.sleep(1.0)
                mouse.release(Button.left)
                keyboard.press('w')
                time.sleep(0.3)
                keyboard.release('w')
        time.sleep(0.1)

def command_listener():
    global current_task, task_params, active
    while running:
        try:
            cmd = input("\nEnter Baritone Command > ").strip()
            if not cmd: continue

            parts = cmd.split()
            command = parts[0].lower()

            if command == "#clear" and len(parts) >= 7:
                coords = [int(p) for p in parts[1:7]]
                task_params = {
                    'minX': min(coords[0], coords[3]),
                    'maxX': max(coords[0], coords[3]),
                    'minY': min(coords[1], coords[4]),
                    'maxY': max(coords[1], coords[4]),
                    'minZ': min(coords[2], coords[5]),
                    'maxZ': max(coords[2], coords[5])
                }
                current_task = 'clear'
                log(f"Queued #clear ({task_params['minX']},{task_params['minY']},{task_params['minZ']}) to ({task_params['maxX']},{task_params['maxY']},{task_params['maxZ']}). Press F8 to start!", send_to_game=True)

            elif command == "#goto" and len(parts) >= 3:
                task_params = {'targetX': int(parts[1]), 'targetZ': int(parts[2])}
                current_task = 'goto'
                log(f"Queued #goto ({task_params['targetX']}, {task_params['targetZ']}). Press F8 to start!", send_to_game=True)

            elif command == "#mine":
                current_task = 'mine'
                log("Queued #mine task. Press F8 to start!", send_to_game=True)

            elif command == "#stop":
                current_task = None
                active = False
                log("Stopped active task.", send_to_game=True)

            else:
                print("Unknown command format! Examples:")
                print("  #clear 374 126 -339 390 145 -313")
                print("  #goto 390 -325")

        except Exception as e:
            print(f"Error: {e}")

def main():
    print("===================================================================")
    print("      BARITONE AI BOT WITH IN-GAME CHAT NOTIFIER (26.2 NATIVE)     ")
    print("===================================================================")
    print(" Commands pop up directly in your Minecraft in-game chat!")
    print(" Press [F8] to Start/Pause | [F9] to Exit")
    print("===================================================================\n")

    listener = KeyboardListener(on_press=on_press)
    listener.start()

    worker = threading.Thread(target=bot_worker, daemon=True)
    worker.start()

    command_listener()

if __name__ == "__main__":
    main()
