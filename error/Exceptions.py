class LauncherFlowInterruptedException(Exception):
    def __init__(self, tag, message):
        super(Exception, self).__init__(message)
        self.caller_tag = tag


class AdbConnectionException(Exception):
    pass
