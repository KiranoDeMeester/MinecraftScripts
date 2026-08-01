from commands.BaseCommand import BaseCommand
from src.BotEngine import BotEngine
from src.ChatNotifier import send_mc_chat

class GotoCommand(BaseCommand):
    name = "goto"
    description = "Navigate player forward (e.g. #goto 10 or #goto 395 -325)"
    signature = "craft goto {steps_or_coords}"

    def handle(self, args):
        if not args:
            send_mc_chat("[Baritone] Usage: #goto <number_of_blocks> (e.g. #goto 10)")
            return

        try:
            if len(args) == 1:
                steps = int(args[0])
            else:
                steps = 15 # Default steps for coordinate pairs

            params = {'steps': steps, 'targetX': int(args[0]), 'targetZ': int(args[1]) if len(args) > 1 else 0}
            bot = BotEngine()
            bot.set_task('goto', params)
            bot.active = True

            msg = f"Navigating {steps} blocks forward..."
            print(f"\033[92m[SUCCESS]\033[0m {msg}")
            send_mc_chat(f"[Baritone] {msg}")

        except ValueError:
            send_mc_chat("[Baritone] Error: Arguments must be numbers! (e.g. #goto 10)")
