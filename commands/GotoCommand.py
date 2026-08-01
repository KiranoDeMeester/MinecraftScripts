from commands.BaseCommand import BaseCommand
from src.BotEngine import BotEngine
from src.ChatNotifier import send_mc_chat

class GotoCommand(BaseCommand):
    name = "goto"
    description = "Navigate player forward or to target coordinates with Sprinting & Auto-Jump"
    signature = "craft goto {steps_or_coords}"

    def handle(self, args):
        if not args:
            send_mc_chat("[Baritone] Usage: #goto <blocks> or #goto <x z> (e.g. #goto 10 or #goto 390 -325)")
            return

        try:
            bot = BotEngine()

            if len(args) == 1:
                # Relative forward steps (e.g. #goto 10)
                steps = int(args[0])
                params = {'mode': 'steps', 'steps': steps}
                msg = f"Sprinting {steps} blocks forward (WASD/ZQSD + Jump)..."
            else:
                # Absolute coordinates (e.g. #goto 390 -325 or #goto 390 126 -325)
                targetX = float(args[0])
                if len(args) >= 3:
                    targetY = float(args[1])
                    targetZ = float(args[2])
                else:
                    targetY = None
                    targetZ = float(args[1])

                params = {'mode': 'coords', 'targetX': targetX, 'targetY': targetY, 'targetZ': targetZ}
                msg = f"Navigating to coordinates ({targetX}, {targetZ}) with Sprinting & Auto-Jump..."

            bot.set_task('goto', params)
            bot.active = True

            print(f"\033[92m[SUCCESS]\033[0m {msg}")
            send_mc_chat(f"[Baritone] {msg}")

        except ValueError:
            send_mc_chat("[Baritone] Error: Coordinates/steps must be numbers! (e.g. #goto 10 or #goto 390 -325)")
