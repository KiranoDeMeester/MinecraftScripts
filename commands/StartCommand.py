from commands.BaseCommand import BaseCommand
from src.BotEngine import BotEngine

class StartCommand(BaseCommand):
    name = "start"
    description = "Start/Resume active queued bot execution"
    signature = "craft start"

    def handle(self, args):
        bot = BotEngine()
        if not bot.active:
            bot.toggle_active()
        else:
            print("\033[93mBot is already running!\033[0m")
