from console.Printer import *

TAG = "AndroidVirtualDevice:"


class AndroidVirtualDevice:
    def __init__(self, avd_schema,
                 port,
                 log_file,
                 android_controller,
                 emulator_controller,
                 adb_controller):
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
            print_error(TAG, "One AVD schema doesn't have name set.")
            quit()

        if self.avd_schema.create_avd_abi == "":
            print_error(TAG, "Parameter 'create_avd_abi' in AVD schema '"
                        + self.avd_schema.avd_name + "' cannot be empty.")
            quit()

        if self.avd_schema.create_avd_target == "":
            print_error(TAG, "Parameter 'create_avd_target' in AVD schema '"
                        + self.avd_schema.avd_name + "' cannot be empty.")
            quit()

        if self.avd_schema.launch_avd_launch_binary_name == "":
            print_error(TAG, "Parameter 'launch_avd_launch_binary_name' in AVD schema '"
                        + self.avd_schema.avd_name + "' cannot be empty.")
            quit()

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

