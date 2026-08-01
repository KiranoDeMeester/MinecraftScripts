from commands.BaseCommand import BaseCommand
from src.BotEngine import BotEngine
from src.ChatNotifier import send_mc_chat

class GotoCommand(BaseCommand):
    name = "goto"
    description = "Navigate player with steps, single coordinate, or (X, Z) / (X, Y, Z) target"
    signature = "craft goto {args}"

    def handle(self, args):
        if not args:
            send_mc_chat("[Baritone] Usage: #goto 10 | #goto <X> | #goto <X> <Z> | #goto <X> <Y> <Z>")
            return

        try:
            bot = BotEngine()
            nums = [float(a) for a in args]

            if len(nums) == 1:
                val = int(nums[0])
                # If val is small positive, treat as forward steps (e.g. #goto 10)
                if 0 < val <= 50:
                    params = {'mode': 'steps', 'steps': val}
                    msg = f"Walking {val} blocks forward..."
                else:
                    # Single X coordinate (e.g. #goto 390)
                    params = {'mode': 'coords', 'targetX': val, 'targetY': None, 'targetZ': None}
                    msg = f"Navigating to target X={val}..."

            elif len(nums) == 2:
                # Target X, Z coordinates (e.g. #goto 390 -325)
                params = {'mode': 'coords', 'targetX': nums[0], 'targetY': None, 'targetZ': nums[1]}
                msg = f"Navigating to coordinates ({nums[0]}, {nums[1]})..."

            else:
                # Target X, Y, Z coordinates (e.g. #goto 390 126 -325)
                params = {'mode': 'coords', 'targetX': nums[0], 'targetY': nums[1], 'targetZ': nums[2]}
                msg = f"Navigating to coordinates ({nums[0]}, {nums[1]}, {nums[2]})..."

            bot.set_task('goto', params)
            bot.active = True

            print(f"\033[92m[SUCCESS]\033[0m {msg}")
            send_mc_chat(f"[Baritone] {msg}")

        except ValueError:
            send_mc_chat("[Baritone] Error: Coordinates must be numbers!")
