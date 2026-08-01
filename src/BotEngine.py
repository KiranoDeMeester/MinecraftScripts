import time
import math
import threading
import sys
from pynput.keyboard import Key, Listener as KeyboardListener
from src.ChatNotifier import send_mc_chat
from src.F3PositionTracker import get_minecraft_position
from src.DirectInput import (
    press_key, release_key, hold_key, click_mouse_left, click_mouse_right, move_mouse,
    KEY_W, KEY_A, KEY_S, KEY_D, KEY_SPACE, KEY_1, KEY_2, KEY_3
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
        release_key(KEY_A)
        release_key(KEY_D)
        release_key(KEY_SPACE)
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

    def _unstuck_maneuver(self):
        """Maneuvers sideways and jumps when blocked by a wall or cliff"""
        print("[UNSTUCK] Wall detected! Executing obstacle avoidance maneuver...")
        send_mc_chat("[Baritone] Obstacle detected! Navigating around wall...")
        
        release_key(KEY_W)
        time.sleep(0.1)
        
        # Turn mouse 45 degrees right
        move_mouse(180, 0)
        time.sleep(0.1)
        
        # Jump and step forward-right around obstacle
        press_key(KEY_W)
        press_key(KEY_D)
        press_key(KEY_SPACE)
        time.sleep(0.6)
        release_key(KEY_SPACE)
        time.sleep(0.4)
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
                    send_mc_chat("[Baritone] [WIP] #clear command is currently under development.")
                    self.current_task = None
                    self.active = False
                    
            time.sleep(0.1)

    def _run_goto_task(self):
        p = self.task_params
        mode = p.get('mode', 'steps')

        time.sleep(0.6) # Allow chat box to close completely

        if mode == 'steps':
            steps = p.get('steps', 10)
            print(f"[GOTO] Walking {steps} blocks forward...")

            press_key(KEY_W)

            start_time = time.time()
            walk_duration = steps * 0.35
            jump_timer = time.time()

            try:
                while self.active and self.current_task == 'goto' and (time.time() - start_time) < walk_duration:
                    if time.time() - jump_timer > 0.7:
                        press_key(KEY_SPACE)
                        time.sleep(0.08)
                        release_key(KEY_SPACE)
                        jump_timer = time.time()

                    time.sleep(0.08)
            finally:
                release_key(KEY_W)

            send_mc_chat(f"[Baritone] Reached destination! Walked {steps} blocks.")
            self.current_task = None
            self.active = False

        elif mode == 'coords':
            targetX = p.get('targetX')
            targetZ = p.get('targetZ')

            pos = get_minecraft_position()
            if not pos:
                print("[GOTO ERROR] Could not read F3 position.")
                send_mc_chat("[Baritone] Error: Could not read player position from F3.")
                self.current_task = None
                self.active = False
                return

            # Fill in missing coordinates from current position
            if targetX is None: targetX = pos['x']
            if targetZ is None: targetZ = pos['z']

            print(f"[GOTO] Navigating to target coordinates ({round(targetX, 1)}, {round(targetZ, 1)})...")

            press_key(KEY_W)

            last_pos = pos
            stuck_count = 0
            jump_timer = time.time()
            f3_timer = time.time()

            try:
                while self.active and self.current_task == 'goto':
                    # Check position, distance, and wall collision every 1.2s
                    if time.time() - f3_timer > 1.2:
                        release_key(KEY_W)
                        current_pos = get_minecraft_position()
                        
                        if current_pos:
                            # Calculate distance traveled since last check
                            moved_dist = math.sqrt((current_pos['x'] - last_pos['x'])**2 + (current_pos['z'] - last_pos['z'])**2)
                            
                            # Check if stuck against a wall
                            if moved_dist < 0.35:
                                stuck_count += 1
                                if stuck_count >= 2:
                                    self._unstuck_maneuver()
                                    stuck_count = 0
                            else:
                                stuck_count = 0

                            last_pos = current_pos

                            # Calculate distance to target
                            dx = targetX - current_pos['x']
                            dz = targetZ - current_pos['z']
                            dist_to_target = math.sqrt(dx*dx + dz*dz)

                            print(f"[F3 TRACKER] Pos: ({round(current_pos['x'],1)}, {round(current_pos['z'],1)}) -> Target Dist: {round(dist_to_target, 1)} blocks")
                            
                            if dist_to_target < 1.8:
                                print("[GOTO] Reached target coordinate destination!")
                                break

                            # Calculate required yaw angle and turn mouse
                            target_yaw = math.atan2(-dx, dz) * (180.0 / math.pi)
                            yaw_diff = target_yaw - current_pos['yaw']
                            
                            turn_pixel = int(yaw_diff * 4.5)
                            if abs(turn_pixel) > 2:
                                move_mouse(turn_pixel, 0)

                        press_key(KEY_W)
                        f3_timer = time.time()

                    # Auto-jump over 1-block steps
                    if time.time() - jump_timer > 0.7:
                        press_key(KEY_SPACE)
                        time.sleep(0.08)
                        release_key(KEY_SPACE)
                        jump_timer = time.time()

                    time.sleep(0.08)
            finally:
                release_key(KEY_W)

            send_mc_chat(f"[Baritone] Reached target destination ({round(targetX, 1)}, {round(targetZ, 1)})!")
            self.current_task = None
            self.active = False
