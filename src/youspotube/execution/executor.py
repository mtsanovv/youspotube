import youspotube.constants as constants

class Execution:
    def __init__(self, config):
        self.config = config


    def execute(self):
        if self.config.is_help_requested():
            self._print_help()
            return
        self._sync_playlists()


    def _sync_playlists(self):
        pass


    def _print_help(self):
        for line in constants.HELP_LINES:
            print(line)