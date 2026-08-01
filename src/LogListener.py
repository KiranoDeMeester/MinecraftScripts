import os
import glob
import time
import re
import threading
from src.ChatNotifier import send_mc_chat

class LogListener:
    def __init__(self, command_registry):
        self.registry = command_registry
        self.running = False
        self.threads = []
        self.processed_lines = set()

    def get_all_log_paths(self):
        paths = []
        std_log = os.path.expanduser(r"~\AppData\Roaming\.minecraft\logs\latest.log")
        if os.path.exists(std_log):
            paths.append(std_log)

        cf_pattern = os.path.expanduser(r"~\curseforge\minecraft\Instances\*\logs\latest.log")
        for cf_log in glob.glob(cf_pattern):
            if cf_log not in paths and os.path.exists(cf_log):
                paths.append(cf_log)

        return paths

    def start(self):
        log_paths = self.get_all_log_paths()
        if not log_paths:
            print("\033[91m[LogListener Error] No active Minecraft latest.log files found.\033[0m")
            return

        self.running = True
        for path in log_paths:
            print(f"\x1b[92m[LogListener] Monitoring log: {path}\x1b[0m")
            t = threading.Thread(target=self._tail_log, args=(path,), daemon=True)
            t.start()
            self.threads.append(t)

    def _tail_log(self, path):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(0, os.SEEK_END)
                file_size = f.tell()
                f.seek(max(0, file_size - 8000))

                while self.running:
                    line = f.readline()
                    if not line:
                        time.sleep(0.15)
                        continue

                    if "[MCA]" in line or "[Baritone]" in line:
                        continue

                    if "[CHAT]" in line and "#" in line:
                        line_id = hash(line.strip())
                        if line_id not in self.processed_lines:
                            self.processed_lines.add(line_id)
                            self._process_chat_line(line)

        except Exception as e:
            print(f"[LogListener Error] {e}")

    def _process_chat_line(self, line):
        match = re.search(r'\[CHAT\]\s*(?:<[^>]+>\s*)?#(\w+)(.*)', line)
        if match:
            cmd_name = match.group(1).lower()
            raw_args = match.group(2).strip().split()

            print(f"\x1b[96m[IN-GAME COMMAND DETECTED]\x1b[0m #{cmd_name} {' '.join(raw_args)}")

            if cmd_name == "help":
                send_mc_chat("[MCA] Commands: #goto <coords/steps> | #clear | #mine | #start | #stop | #help")
            elif cmd_name in self.registry:
                self.registry[cmd_name].handle(raw_args)
            else:
                send_mc_chat(f"[MCA] Unknown command '#{cmd_name}'. Type #help for command list.")
