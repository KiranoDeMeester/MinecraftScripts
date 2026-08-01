import time
import math
import threading
import sys
from pynput.keyboard import Key, Listener as KeyboardListener
from src.ChatNotifier import send_mc_chat
from src.DirectInput import (
    press_key, release_key, hold_key, click_mouse_left, click_mouse_right, move_mouse,
    KEY_W, KEY_A, KEY_S, KEY_D, KEY_1, KEY_2, KEY_3
)

class BotEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BotEngine, cls).__new__(cls)
            cls._instance.init_engine()
        return cls._instance

    def init_engine(self):
        self.active = False
        self.running = True
        self.current_task = None
        self.task_params = {}
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        self.listener = KeyboardListener(on_press=self._on_press)
        self.listener.start()

    def _on_press(self, key):
        try:
            if key == Key.f8:
                self.toggle_active()
            elif key == Key.f9:
                self.stop_engine()
        except Exception:
            pass

    def toggle_active(self):
        self.active = not self.active
        if self.active:
            send_mc_chat("[Baritone] Bot STARTED!")
            print("\033[92m[ACTIVE] Bot started!\033[0m")
        else:
            send_mc_chat("[Baritone] Bot PAUSED. Press F8 or #start to resume.")
            print("\033[93m[PAUSED] Bot paused.\033[0m")

    def stop_engine(self):
        self.active = False
        self.current_task = None
        release_key(KEY_W)
        send_mc_chat("[Baritone] Task STOPPED.")
        print("\033[91m[STOPPED] Task stopped.\033[0m")

    def set_task(self, task_name, params):
        self.current_task = task_name
        self.task_params = params

    def _eat_food(self):
        send_mc_chat("[Baritone] Eating bread from Slot 1...")
        time.sleep(0.5)
        
        press_key(KEY_1)
        time.sleep(0.1)
        release_key(KEY_1)
        time.sleep(0.2)
        
        click_mouse_right(duration=3.2)
        time.sleep(0.2)
        
        press_key(KEY_2)
        time.sleep(0.1)
        release_key(KEY_2)

    def _equip_tool(self, category):
        if category == 'pickaxe':
            press_key(KEY_2)
            time.sleep(0.05)
            release_key(KEY_2)
        elif category == 'shovel':
            press_key(KEY_3)
            time.sleep(0.05)
            release_key(KEY_3)
        time.sleep(0.1)

    def _worker_loop(self):
        eat_timer = time.time()
        
        while self.running:
            if self.active and self.current_task:
                if time.time() - eat_timer > 60:
                    self._eat_food()
                    eat_timer = time.time()

                if self.current_task == 'clear':
                    self._run_clear_task()
                elif self.current_task == 'goto':
                    self._run_goto_task()
                    
            time.sleep(0.1)

    def _run_clear_task(self):
        p = self.task_params
        minX, minY, minZ = p['minX'], p['minY'], p['minZ']
        maxX, maxY, maxZ = p['maxX'], p['maxY'], p['maxZ']

        total_blocks = (abs(maxX - minX) + 1) * (abs(maxY - minY) + 1) * (abs(maxZ - minZ) + 1)
        mined_blocks = 0

        time.sleep(1.0)

        for y in range(maxY, minY - 1, -1):
            if not self.active: return
            
            for x in range(minX, maxX + 1):
                for z in range(minZ, maxZ + 1):
                    if not self.active: return

                    self._equip_tool('shovel' if y > 132 else 'pickaxe')

                    click_mouse_left(duration=0.8)

                    press_key(KEY_W)
                    time.sleep(0.35)
                    release_key(KEY_W)

                    mined_blocks += 1
                    if mined_blocks % 20 == 0:
                        send_mc_chat(f"[Baritone] Clear progress: {int((mined_blocks/total_blocks)*100)}%")
                        time.sleep(0.5)

        send_mc_chat("[Baritone] 🎉 #clear command completed successfully!")
        self.current_task = None
        self.active = False

    def _run_goto_task(self):
        p = self.task_params
        steps = p.get('steps', 15)

        # Wait 1 second for chat box to close completely
        time.sleep(1.0)

        print(f"[GOTO] Continuous walk for {steps} blocks...")

        # Hold W key continuously (exact same mechanism as test_move.py)
        press_key(KEY_W)
        
        start_time = time.time()
        walk_duration = steps * 0.35

        try:
            while self.active and self.current_task == 'goto' and (time.time() - start_time) < walk_duration:
                click_mouse_left(duration=0.4)
                time.sleep(0.1)
        finally:
            release_key(KEY_W)

        send_mc_chat(f"[Baritone] Reached destination! Completed {steps} steps.")
        self.current_task = None
        self.active = False
