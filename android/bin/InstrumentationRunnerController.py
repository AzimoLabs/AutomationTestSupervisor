from android.bin.command.InstrumentationRunnerCommand import *
from android.bin.command.AdbCommand import *
from console.ShellHelper import *
from console.Printer import *
from system.mapper.PathMapper import *
from settings.Settings import *

TAG = "InstrumentationRunnerController:"


class InstrumentationRunnerController:
    adb_bin = None

    def __init__(self):
        self.adb_bin = clean_path(add_ending_slash(Settings.SDK_DIR) + "platform-tools/adb")

        if os.path.isfile(self.adb_bin):
            print_message(TAG, "ADB binary file found at '" + self.adb_bin + "'.")
        else:
            print_error(TAG, "Unable to find ADB binary at '" + self.adb_bin + "'.")
            quit()

    def assemble_run_test_package_cmd(self, device_name, test_package):
        return InstrumentationRunnerCommand.RUN_TEST_PACKAGE.format(self.adb_bin,
                                                                    AdbCommand.SPECIFIC_DEVICE + " " + device_name,
                                                                    test_package,
                                                                    Settings.INSTRUMENTATION_RUNNER)
