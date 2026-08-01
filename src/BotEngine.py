import time
import math
import threading
import sys
import ctypes
from src.ChatNotifier import send_mc_chat
from src.F3PositionTracker import get_minecraft_position
from src.DirectInput import (
    press_key, release_key, hold_key, click_mouse_left, click_mouse_right, move_mouse,
    KEY_W, KEY_A, KEY_S, KEY_D, KEY_SPACE, KEY_1, KEY_2, KEY_3
)

# Windows Virtual Key Codes
VK_F8 = 0x77     # [F8] Start / Pause Toggle
VK_F9 = 0x78     # [F9] Emergency Stop
VK_ESCAPE = 0x1B # [ESC] Manual Cancel
VK_S = 0x53      # [S] Manual Cancel (Pull back)

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
        self.saved_task = None # Persistent task memory for F8 / #start resume!
        
        # Hardware key monitor thread (F8, F9, ESC, S)
        self.hotkey_thread = threading.Thread(target=self._hotkey_monitor_loop, daemon=True)
        self.hotkey_thread.start()

        # Worker loop thread
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def set_task(self, task_name, params):
        self.current_task = task_name
        self.task_params = params
        self.saved_task = {'name': task_name, 'params': params} # Save task for resume!
        print(f"\033[96m[TASK SAVED]\033[0m Saved '{task_name}' task to memory.")

    def _hotkey_monitor_loop(self):
        """Continuously monitors Windows physical hardware state for F8, F9, ESC, and S keys"""
        GetAsyncKeyState = ctypes.windll.user32.GetAsyncKeyState
        
        last_f8 = False
        last_f9 = False
        
        while self.running:
            try:
                f8_state = (GetAsyncKeyState(VK_F8) & 0x8000) != 0
                f9_state = (GetAsyncKeyState(VK_F9) & 0x8000) != 0
                esc_state = (GetAsyncKeyState(VK_ESCAPE) & 0x8000) != 0
                s_state = (GetAsyncKeyState(VK_S) & 0x8000) != 0

                # F8 Toggle (on press edge)
                if f8_state and not last_f8:
                    self.toggle_active()
                last_f8 = f8_state

                # F9 Emergency Stop (on press edge)
                if f9_state and not last_f9:
                    self.stop_engine()
                last_f9 = f9_state

                # ESC or S Manual Override (while bot is active)
                if self.active and (esc_state or s_state):
                    print("\033[93m[OVERRIDE] Player pressed ESC / S key! Pausing task...\033[0m")
                    self.active = False
                    self.current_task = None
                    release_key(KEY_W)
                    release_key(KEY_A)
                    release_key(KEY_D)
                    release_key(KEY_SPACE)
                    send_mc_chat("[MCA] Manual override (ESC/S). Task paused. Press F8 or #start to resume.")

            except Exception:
                pass
                
            time.sleep(0.05)

    def toggle_active(self):
        self.active = not self.active
        if self.active:
            # Resume saved task if current_task is empty
            if not self.current_task and self.saved_task:
                self.current_task = self.saved_task['name']
                self.task_params = self.saved_task['params']
                send_mc_chat(f"[MCA] Resumed task '{self.current_task}'!")
                print(f"\033[92m[RESUMED]\033[0m Resumed saved task '{self.current_task}'!")
            else:
                send_mc_chat("[MCA] Bot STARTED!")
                print("\033[92m[ACTIVE]\033[0m Bot started!")
        else:
            send_mc_chat("[MCA] Bot PAUSED. Press F8 or #start to resume.")
            print("\033[93m[PAUSED]\033[0m Bot paused.")

    def stop_engine(self):
        self.active = False
        self.current_task = None
        self.saved_task = None # Clear saved task on emergency stop!
        release_key(KEY_W)
        release_key(KEY_A)
        release_key(KEY_D)
        release_key(KEY_SPACE)
        send_mc_chat("[MCA] Task STOPPED and cleared.")
        print("\033[91m[STOPPED]\033[0m Task stopped & memory cleared.")

    def _eat_food(self):
        send_mc_chat("[MCA] Eating bread from Slot 1...")
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

    def _unstuck_maneuver(self):
        """Maneuvers sideways and jumps when blocked by a tall wall"""
        print("[UNSTUCK] High wall detected! Navigating around wall...")
        send_mc_chat("[MCA] Obstacle detected! Navigating around wall...")
        
        release_key(KEY_W)
        time.sleep(0.1)
        
        move_mouse(180, 0) # Turn 45 degrees right
        time.sleep(0.1)
        
        press_key(KEY_W)
        press_key(KEY_D)
        press_key(KEY_SPACE)
        time.sleep(0.5)
        release_key(KEY_SPACE)
        time.sleep(0.3)
        release_key(KEY_D)
        release_key(KEY_W)
        time.sleep(0.1)

    def _worker_loop(self):
        eat_timer = time.time()
        
        while self.running:
            if self.active and self.current_task:
                if time.time() - eat_timer > 60:
                    self._eat_food()
                    eat_timer = time.time()

                if self.current_task == 'goto':
                    self._run_goto_task()
                elif self.current_task == 'clear':
                    send_mc_chat("[MCA] [WIP] #clear command is currently under development.")
                    self.current_task = None
                    self.saved_task = None
                    self.active = False
                    
            time.sleep(0.1)

    def _run_goto_task(self):
        p = self.task_params
        mode = p.get('mode', 'steps')

        time.sleep(0.6) # Allow chat box to close completely

        if mode == 'steps':
            steps = p.get('steps', 10)
            print(f"[GOTO] Smooth walking {steps} blocks forward...")

            press_key(KEY_W)
            start_time = time.time()
            walk_duration = steps * 0.35

            try:
                while self.active and self.current_task == 'goto' and (time.time() - start_time) < walk_duration:
                    time.sleep(0.08)
            finally:
                release_key(KEY_W)

            if self.active:
                send_mc_chat(f"[MCA] Reached destination! Walked {steps} blocks.")
                self.saved_task = None # Task finished successfully! Clear memory!
            self.current_task = None
            self.active = False

        elif mode == 'coords':
            targetX = p.get('targetX')
            targetZ = p.get('targetZ')

            pos = get_minecraft_position()
            if not pos:
                send_mc_chat("[MCA] Error: Could not read player position from F3.")
                self.current_task = None
                self.active = False
                return

            if targetX is None: targetX = pos['x']
            if targetZ is None: targetZ = pos['z']

            print(f"[GOTO] Navigating to coordinates ({round(targetX, 1)}, {round(targetZ, 1)})...")

            press_key(KEY_W)

            last_pos = pos
            stuck_count = 0
            check_timer = time.time()

            try:
                while self.active and self.current_task == 'goto':
                    if time.time() - check_timer > 0.8:
                        release_key(KEY_W)
                        time.sleep(0.05)

                        current_pos = get_minecraft_position()
                        
                        if current_pos:
                            moved_dist = math.sqrt((current_pos['x'] - last_pos['x'])**2 + (current_pos['z'] - last_pos['z'])**2)
                            
                            if moved_dist < 0.05:
                                stuck_count += 1
                                print(f"[SMART JUMP] Step collision detected (moved {round(moved_dist,3)} blocks). Jumping!")
                                press_key(KEY_SPACE)
                                time.sleep(0.08)
                                release_key(KEY_SPACE)

                                if stuck_count >= 3:
                                    self._unstuck_maneuver()
                                    stuck_count = 0
                            else:
                                stuck_count = 0

                            last_pos = current_pos

                            # Distance to target
                            dx = targetX - current_pos['x']
                            dz = targetZ - current_pos['z']
                            dist_to_target = math.sqrt(dx*dx + dz*dz)

                            print(f"[F3 TRACKER] Pos: ({round(current_pos['x'],1)}, {round(current_pos['z'],1)}) -> Target Dist: {round(dist_to_target, 1)} blocks")
                            
                            if dist_to_target < 1.8:
                                print("[GOTO] Reached coordinate destination!")
                                break

                            # Recalculate yaw & turn mouse
                            target_yaw = math.atan2(-dx, dz) * (180.0 / math.pi)
                            yaw_diff = target_yaw - current_pos['yaw']
                            
                            turn_pixel = int(yaw_diff * 4.5)
                            if abs(turn_pixel) > 2:
                                move_mouse(turn_pixel, 0)

                        press_key(KEY_W)
                        check_timer = time.time()

                    time.sleep(0.08)
            finally:
                release_key(KEY_W)

            if self.active:
                send_mc_chat(f"[MCA] Reached target destination ({round(targetX, 1)}, {round(targetZ, 1)})!")
                self.saved_task = None # Task finished successfully! Clear memory!
            self.current_task = None
            self.active = False
