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
from src.MinecraftChecker import is_minecraft_running
from src.DirectInput import press_key, release_key, click_mouse_left, KEY_W

COMMAND_REGISTRY = {
    'clear': ClearCommand(),
    'goto': GotoCommand(),
    'mine': MineCommand(),
    'start': StartCommand(),
    'stop': StopCommand(),
    'help': HelpCommand(),
    'list': HelpCommand()
}

def run_hardware_test():
    print("\n-------------------------------------------------------------------")
    print(" HARDWARE MOVEMENT TEST:")
    print(" This test verifies your DirectInput hardware controls by walking")
    print(" 3 blocks forward and swinging your pickaxe.")
    print("-------------------------------------------------------------------")
    choice = input(" Would you like to run the Hardware Movement Test? [y/N]: ").strip().lower()
    
    if choice in ['y', 'yes']:
        print("\n [!] Switch to your Minecraft game window NOW!")
        print(" Test starting in 3 seconds...")
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)

        print("\n >>> [TEST] Walking 3 blocks forward... <<<")
        press_key(KEY_W)
        time.sleep(1.2)
        release_key(KEY_W)

        print(" >>> [TEST] Swinging pickaxe... <<<")
        click_mouse_left(duration=0.8)

        print(" [✓] Hardware Test Completed successfully!\n")
    else:
        print(" [+] Skipping Hardware Test...\n")

def start_interactive_daemon():
    print("""
===================================================================
               MINECRAFT ARTISAN INTERACTIVE DAEMON                
                 (Minecraft 26.2 Native Edition)                   
===================================================================""")

    # Step 1: Check if Minecraft process is open
    if is_minecraft_running():
        print(" [✓] Minecraft process detected! (javaw.exe / Minecraft.exe is active)")
    else:
        print(" [!] Warning: Minecraft is not currently detected.")
        print("     Please launch Minecraft 26.2 and open your world.")

    # Step 2: Ask player for hardware test (skippable)
    run_hardware_test()

    # Step 3: Display available Artisan commands
    HelpCommand().handle([])

    # Step 4: Start live log listener for in-game MC chat and CMD
    print(" [DAEMON ONLINE] Listening for commands directly in Minecraft Chat!")
    print(" Type #help, #clear, #start, or #stop in Minecraft chat anytime!\n")

    listener = LogListener(COMMAND_REGISTRY)
    listener.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n [DAEMON OFFLINE] Stopped Minecraft Artisan Daemon.")

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
