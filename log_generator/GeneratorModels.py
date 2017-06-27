class LogPackage:
    def __init__(self):
        self.name = None
        self.logs = None


class Log:
    def __init__(self):
        self.name = None
        self.package_name = None
        self.device = None
        self.duration = None
        self.status = None
        self.error = None
        self.error_type = None
        self.logcat = None
        self.recording = None
