from youspotube.utils import Help

class Execution:
    def __init__(self, config):
        self.config = config
    def execute(self):
        if self.config.is_help:
            Help.print()
            return
            