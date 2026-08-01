from commands.BaseCommand import BaseCommand
from src.ChatNotifier import send_mc_chat

class GotoCommand(BaseCommand):
    name = "goto"
    description = "Navigate player toward target coordinates (WORK IN PROGRESS)"
    signature = "craft goto {x} {z}"

    def handle(self, args):
        msg = "[WIP] #goto command is currently under development."
        print(f"\033[93m{msg}\033[0m")
        send_mc_chat(f"[Baritone] {msg}")
