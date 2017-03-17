class OutsideSessionVirtualDevice:
    def __init__(self, adb_name, status, adb_controller):
        self.adb_controller = adb_controller
        self.adb_name = adb_name
        self.status = status

    def install_apk(self, apk_file):
        return self.adb_controller.install_apk(self.adb_name, apk_file)

    def get_property(self, device_property):
        return self.adb_controller.get_property(self.adb_name, device_property)

    def kill(self):
        return self.adb_controller.kill_device(self.adb_name)