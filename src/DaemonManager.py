import os
import sys
import json
import time
import subprocess

QUEUE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "command_queue.json")
LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daemon.pid")

def is_daemon_running():
    if not os.path.exists(LOCK_FILE):
        return False
    try:
        with open(LOCK_FILE, "r") as f:
            pid = int(f.read().strip())
        # Check if PID is alive on Windows
        output = subprocess.check_output(f'tasklist /FI "PID eq {pid}"', shell=True).decode()
        return "python" in output.lower()
    except Exception:
        return False

def ensure_daemon_running():
    if not is_daemon_running():
        craft_py = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "craft.py")
        print("[+] Starting Minecraft Artisan Daemon in background...")
        # Launch detached background process on Windows
        subprocess.Popen([sys.executable, craft_py, "daemon"], 
                         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                         close_fds=True)
        time.sleep(1.5)

def send_command_to_queue(command_name, args):
    ensure_daemon_running()
    cmd_data = {
        "command": command_name,
        "args": args,
        "timestamp": time.time()
    }
    with open(QUEUE_FILE, "w") as f:
        json.dump(cmd_data, f)
    print(f"[SUCCESS] Command '{command_name}' sent to background daemon!")

def get_queued_command():
    if not os.path.exists(QUEUE_FILE):
        return None
    try:
        with open(QUEUE_FILE, "r") as f:
            data = json.load(f)
        os.remove(QUEUE_FILE)
        return data
    except Exception:
        return None

def write_daemon_pid():
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

def remove_daemon_pid():
    if os.path.exists(LOCK_FILE):
        try: os.remove(LOCK_FILE)
        except Exception: pass
