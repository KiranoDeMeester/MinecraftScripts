from commands.BaseCommand import BaseCommand

class HelpCommand(BaseCommand):
    name = "help"
    description = "Display list of available craft commands and usage details"
    signature = "craft help"

    def handle(self, args):
        print("""
===================================================================
                  MINECRAFT ARTISAN CLI v1.0.0                    
                 (Minecraft 26.2 Native Edition)                  
===================================================================

USAGE:
  mca <command> [arguments]   (or type #command in Minecraft chat!)

AVAILABLE COMMANDS:
  goto     Navigate player forward with WASD/ZQSD + Auto-Jumping
           Example: mca goto 10 (or #goto 10 in game)

  start    Start / Resume active queued bot task
           Example: mca start (or press F8 / #start in game)

  stop     Halt and cancel active bot task
           Example: mca stop (or press F9 / #stop in game)

  help     Display this Artisan help menu
           Example: mca help (or #help in game)

WORK IN PROGRESS COMMANDS:
  clear    [WORK IN PROGRESS] Excavate a 3D bounding box region
           Example: mca clear 374 126 -339 390 145 -313

  mine     [WORK IN PROGRESS] Mine specific block type
           Example: mca mine iron_ore

HOTKEYS:
  [F8] -> Start / Pause execution directly inside Minecraft
  [F9] -> Emergency Stop & Exit
===================================================================
""")
