class BaseCommand:
    name = ""
    description = ""
    signature = ""

    def handle(self, args):
        raise NotImplementedError("Each command must implement the handle() method.")
