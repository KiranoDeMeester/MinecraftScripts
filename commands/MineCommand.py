from commands.BaseCommand import BaseCommand
from src.ChatNotifier import send_mc_chat

class MineCommand(BaseCommand):
    name = "mine"
    description = "Automatically search and mine specific block types (WORK IN PROGRESS)"
    signature = "craft mine {block_type}"

    def handle(self, args):
        block = args[0] if args else "target blocks"
        msg = f"[WIP] #mine {block} is currently under development."
        print(f"\033[93m{msg}\033[0m")
        send_mc_chat(f"[MCA] {msg}")
