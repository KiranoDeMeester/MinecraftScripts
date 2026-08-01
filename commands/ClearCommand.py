from commands.BaseCommand import BaseCommand
from src.BotEngine import BotEngine
from src.ChatNotifier import send_mc_chat

class ClearCommand(BaseCommand):
    name = "clear"
    description = "Excavate a 3D bounding box region (minX minY minZ maxX maxY maxZ)"
    signature = "craft clear {minX} {minY} {minZ} {maxX} {maxY} {maxZ}"

    def handle(self, args):
        if len(args) < 6:
            print("\033[91mError: #clear requires 6 coordinate arguments!\033[0m")
            send_mc_chat("[Baritone] Error: #clear requires 6 coordinates! (minX minY minZ maxX maxY maxZ)")
            return

        try:
            coords = [int(a) for a in args[:6]]
            minX, maxX = min(coords[0], coords[3]), max(coords[0], coords[3])
            minY, maxY = min(coords[1], coords[4]), max(coords[1], coords[4])
            minZ, maxZ = min(coords[2], coords[5]), max(coords[2], coords[5])

            params = {
                'minX': minX, 'maxX': maxX,
                'minY': minY, 'maxY': maxY,
                'minZ': minZ, 'maxZ': maxZ
            }

            bot = BotEngine()
            bot.set_task('clear', params)
            
            # Auto-start excavation immediately!
            bot.active = True

            msg = f"Started #clear excavation from ({minX},{minY},{minZ}) to ({maxX},{maxY},{maxZ})"
            print(f"\033[92m[SUCCESS]\033[0m {msg}")
            send_mc_chat(f"[Baritone] {msg}")

        except ValueError:
            print("\033[91mError: All coordinates must be integers!\033[0m")
            send_mc_chat("[Baritone] Error: All coordinates must be numbers!")
