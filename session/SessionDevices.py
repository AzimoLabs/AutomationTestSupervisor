from error.Exceptions import LauncherFlowInterruptedException


class OutsideSessionDevice:
    def __init__(self, adb_name, status, adb_controller):
        self.adb_controller = adb_controller
        self.adb_name = adb_name
        self.status = status

    def install_apk(self, apk_file):
        return self.adb_controller.install_apk(self.adb_name, apk_file)


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


class SessionVirtualDevice:
    TAG = "SessionVirtualDevice:"

    def __init__(self, avd_schema, port, log_file, android_controller, emulator_controller, adb_controller):
        self.android_controller = android_controller
        self.emulator_controller = emulator_controller
        self.adb_controller = adb_controller
        self.avd_schema = avd_schema

        self._check_avd_schema()

        self.port = port
        self.log_file = log_file
        self.adb_name = "emulator-" + str(self.port)
        self.status = "not-launched"

    def _check_avd_schema(self):
        if self.avd_schema.avd_name == "":
            message = "One AVD schema doesn't have name set."
            raise LauncherFlowInterruptedException(self.TAG, message)

        if self.avd_schema.create_avd_package == "":
            message = "Parameter 'create_avd_package' in AVD schema {} cannot be empty."
            message = message.format(self.avd_schema.avd_name)
            raise LauncherFlowInterruptedException(self.TAG, message)

        if self.avd_schema.launch_avd_launch_binary_name == "":
            message = "Parameter 'launch_avd_launch_binary_name' in AVD schema {} cannot be empty."
            message = message.format(self.avd_schema.avd_name)
            raise LauncherFlowInterruptedException(self.TAG, message)

    def create(self):
        return self.android_controller.create_avd(self.avd_schema)

    def delete(self):
        return self.android_controller.delete_avd(self.avd_schema)

    def launch(self):
        return self.emulator_controller.launch_avd(self.avd_schema, self.port, self.log_file)

    def get_property(self, device_property):
        return self.adb_controller.get_property(self.adb_name, device_property)

    def kill(self):
        return self.adb_controller.kill_device(self.adb_name)

    def apply_config_ini(self):
        return self.emulator_controller.apply_config_to_avd(self.avd_schema)

    def install_apk(self, apk_file):
        return self.adb_controller.install_apk(self.adb_name, apk_file)
