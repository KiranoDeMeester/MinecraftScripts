from commands.BaseCommand import BaseCommand
from src.BotEngine import BotEngine
from src.ChatNotifier import send_mc_chat

class GotoCommand(BaseCommand):
    name = "goto"
    description = "Navigate player forward with WASD/ZQSD movement & auto-jumping"
    signature = "craft goto {steps_or_coords}"

    def handle(self, args):
        if not args:
            send_mc_chat("[Baritone] Usage: #goto <number_of_blocks> (e.g. #goto 10)")
            return

        try:
            steps = int(args[0])
            params = {'steps': steps}
            
            bot = BotEngine()
            bot.set_task('goto', params)
            bot.active = True

            msg = f"Navigating {steps} blocks forward (WASD/ZQSD + Jump)..."
            print(f"\033[92m[SUCCESS]\033[0m {msg}")
            send_mc_chat(f"[Baritone] {msg}")

        except ValueError:
            send_mc_chat("[Baritone] Error: Steps must be a number! (e.g. #goto 10)")
