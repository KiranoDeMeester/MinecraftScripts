from commands.BaseCommand import BaseCommand
from src.BotEngine import BotEngine

class StopCommand(BaseCommand):
    name = "stop"
    description = "Halt and cancel active bot task"
    signature = "craft stop"

    def handle(self, args):
        bot = BotEngine()
        bot.stop_engine()
