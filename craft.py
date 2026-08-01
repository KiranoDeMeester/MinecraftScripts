#!/usr/bin/env python3
"""
===================================================================
MINECRAFT SCRIPTS - ARTISAN CLI & INTERACTIVE DAEMON ENGINE
===================================================================
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from commands.ClearCommand import ClearCommand
from commands.GotoCommand import GotoCommand
from commands.MineCommand import MineCommand
from commands.StartCommand import StartCommand
from commands.StopCommand import StopCommand
from commands.HelpCommand import HelpCommand
from src.LogListener import LogListener

COMMAND_REGISTRY = {
    'clear': ClearCommand(),
    'goto': GotoCommand(),
    'mine': MineCommand(),
    'start': StartCommand(),
    'stop': StopCommand(),
    'help': HelpCommand(),
    'list': HelpCommand()
}

def start_interactive_daemon():
    print("""
===================================================================
               MINECRAFT ARTISAN INTERACTIVE DAEMON                
                 (Minecraft 26.2 Native Edition)                   
===================================================================
[DAEMON ONLINE] Listening for commands directly in Minecraft Chat!
  - Type #help in Minecraft chat to see commands
  - Type #goto <steps> (e.g. #goto 10) in Minecraft chat to walk
  - Type #clear <coords> in Minecraft chat to excavate
  - Type #start or #stop in Minecraft chat
  - Hotkeys: [F8] Start/Pause | [F9] Exit
===================================================================
""")
    listener = LogListener(COMMAND_REGISTRY)
    listener.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[DAEMON OFFLINE] Stopped Minecraft Artisan Daemon.")

def main():
    if len(sys.argv) < 2 or sys.argv[1].lower() in ['listen', 'daemon', 'watch', 'start']:
        start_interactive_daemon()
        return

    cmd_name = sys.argv[1].lower().replace('#', '')
    cmd_args = sys.argv[2:]

    if cmd_name == 'help':
        HelpCommand().handle(cmd_args)
    elif cmd_name in COMMAND_REGISTRY:
        COMMAND_REGISTRY[cmd_name].handle(cmd_args)
    else:
        print(f"Error: Command '{cmd_name}' is not defined.")
        print("Run 'mca help' to see available commands.\n")

if __name__ == "__main__":
    main()
