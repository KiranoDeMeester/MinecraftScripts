from commands.BaseCommand import BaseCommand
from src.ChatNotifier import send_mc_chat

class ClearCommand(BaseCommand):
    name = "clear"
    description = "Excavate 3D bounding box region (WORK IN PROGRESS)"
    signature = "craft clear {minX} {minY} {minZ} {maxX} {maxY} {maxZ}"

    def handle(self, args):
        msg = "[WIP] #clear command is currently under development."
        print(f"\033[93m{msg}\033[0m")
        send_mc_chat(f"[MCA] {msg}")
