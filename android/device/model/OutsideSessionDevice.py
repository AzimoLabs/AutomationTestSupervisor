class OutsideSessionDevice:
    def __init__(self, adb_name, status, adb_controller):
        self.adb_controller = adb_controller
        self.adb_name = adb_name
        self.status = status

    def install_apk(self, apk_file):
        return self.adb_controller.install_apk(self.adb_name, apk_file)
