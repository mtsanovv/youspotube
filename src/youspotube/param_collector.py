class BaseParameterCollector:
    def __init__(self, config):
        self.config = config

class CfgFileParameterCollector(BaseParameterCollector):
    def collect(self):
        pass

class CmdLineParameterCollector(BaseParameterCollector):
    def collect(self):
        pass