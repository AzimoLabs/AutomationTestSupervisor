import os
import re

from android.bin.AndroidShellCommandAssemblers import (
    AaptCommandAssembler,
    AdbCommandAssembler
)

from android.bin.AndroidShellCommands import (AaptCommand, AdbCommand, AvdManagerCommand, EmulatorCommand,
                                              GradleCommand, InstrumentationRunnerCommand)
from error.Exceptions import LauncherFlowInterruptedException

from settings import GlobalConfig

from system.bin.SystemShellCommands import GeneralCommand
from system.console import (Printer, ShellHelper)
from system.file.FileUtils import (clean_path, add_ending_slash, )


class AaptController:
    TAG = "AaptController:"

    aapt_bin = None

    def __init__(self):
        build_tools = self._find_latest_build_tools()
        self.aapt_bin = clean_path(add_ending_slash(GlobalConfig.SDK_DIR) + "build-tools/" + build_tools + "/aapt")
        self._check_bin_directory()
        self.aapt_command_assembler = AdbCommandAssembler()

    def _find_latest_build_tools(self):
        build_tools = os.listdir(clean_path(add_ending_slash(GlobalConfig.SDK_DIR) + "build-tools"))
        build_tools = [build_tool for build_tool in build_tools if build_tool[0].isdigit()]
        build_tools_folder_with_highest_ver = None
        Printer.system_message(self.TAG, "Available Android SDK Build-Tools versions: " + str(build_tools))
        for build_tools_folder in build_tools:
            if build_tools_folder_with_highest_ver is None:
                build_tools_folder_with_highest_ver = build_tools_folder
                continue

            ver = int(re.sub("[^0-9]", "", build_tools_folder))
            highest_ver = int(re.sub("[^0-9]", "", build_tools_folder_with_highest_ver))

            if ver > highest_ver:
                build_tools_folder_with_highest_ver = build_tools_folder
        if build_tools_folder_with_highest_ver is None:
            message = "Android SDK Build-Tools not found. Launcher will quit."
            raise LauncherFlowInterruptedException(self.TAG, message)

        else:
            Printer.message_highlighted(self.TAG, "Android SDK Build-Tools with latest version were selected: ",
                                        str(build_tools_folder_with_highest_ver))
        return build_tools_folder_with_highest_ver

    def _check_bin_directory(self):
        if os.path.isfile(self.aapt_bin):
            Printer.system_message(self.TAG, "Aapt binary file found at '" + self.aapt_bin + "'.")
        else:
            message = "Unable to find Aapt binary at '{}'."
            message = message.format(self.aapt_bin)
            raise LauncherFlowInterruptedException(self.TAG, message)

    def dump_badging(self, apk_name):
        dump_badging_cmd = "{} {}".format(self.aapt_bin, AaptCommand.DUMP_BADGING.format(apk_name))
        return ShellHelper.execute_shell(dump_badging_cmd, False, False)


class AdbController:
    TAG = "AdbController:"

    adb_bin = None

    def __init__(self):
        self.adb_bin = clean_path(add_ending_slash(GlobalConfig.SDK_DIR) + "platform-tools/adb")

        if os.path.isfile(self.adb_bin):
            Printer.system_message(self.TAG, "ADB binary file found at '" + self.adb_bin + "'.")
        else:
            message = "Unable to find ADB binary at '{}'."
            message = message.format(self.adb_bin)
            raise LauncherFlowInterruptedException(self.TAG, message)

    def start_server(self):
        start_server_cmd = "{} {}".format(self.adb_bin, AdbCommand.START_SERVER)
        return ShellHelper.execute_shell(start_server_cmd, True, True)

    def kill_server(self):
        kill_server_cmd = "{} {}".format(self.adb_bin, AdbCommand.KILL_SERVER)
        return ShellHelper.execute_shell(kill_server_cmd, True, True)

    def devices(self):
        devices_cmd = "{} {}".format(self.adb_bin, AdbCommand.DEVICES)
        return ShellHelper.execute_shell(devices_cmd, False, False)

    def wait_for_device(self):
        waif_for_device_cmd = "{} {}".format(self.adb_bin, AdbCommand.WAIT_FOR_DEVICE)
        return ShellHelper.execute_shell(waif_for_device_cmd, False, False)

    def kill_device(self, device_adb_name):
        kill_device_cmd = "{} {} {} {}".format(self.adb_bin, AdbCommand.SPECIFIC_DEVICE, device_adb_name,
                                               AdbCommand.KILL_DEVICE)
        return ShellHelper.execute_shell(kill_device_cmd, True, False)

    def install_apk(self, device_adb_name, apk_name):
        install_apk_cmd = "{} {} {} {}".format(self.adb_bin, AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                               AdbCommand.INSTALL_APK.format(apk_name), GeneralCommand.CHANGE_THREAD)
        return ShellHelper.execute_shell(install_apk_cmd, True, False)

    def get_property(self, device_adb_name, device_property):
        get_property_cmd = "{} {} {} {}".format(self.adb_bin, AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                                AdbCommand.GET_PROPERTY, device_property)
        return ShellHelper.execute_shell(get_property_cmd, False, False)


class AvdManagerController:
    TAG = "AvdManagerController:"

    avdmanager_bin = None

    def __init__(self):
        self.avdmanager_bin = clean_path(add_ending_slash(GlobalConfig.SDK_DIR) + "tools/bin/avdmanager")

        if os.path.isfile(self.avdmanager_bin):
            Printer.system_message(self.TAG, "AvdManager binary file found at '" + self.avdmanager_bin + "'.")
        else:
            message = "Unable to find ADB binary at '{}'."
            message = message.format(self.avdmanager_bin)
            raise LauncherFlowInterruptedException(self.TAG, message)

    def list_avd(self):
        list_avd_cmd = "{} {}".format(self.avdmanager_bin, AvdManagerCommand.LIST_AVD)
        return ShellHelper.execute_shell(list_avd_cmd, False, False)

    def delete_avd(self, avd_schema):
        delete_avd_cmd = "{} {}".format(self.avdmanager_bin, AvdManagerCommand.DELETE_AVD.format(avd_schema.avd_name))
        return ShellHelper.execute_shell(delete_avd_cmd, True, True)

    def create_avd(self, avd_schema):
        part_answer_no = GeneralCommand.ANSWER_NO
        part_create_avd = AvdManagerCommand.CreateAvdCommandPart.AVD_CREATE
        part_name = AvdManagerCommand.CreateAvdCommandPart.AVD_NAME.format(avd_schema.avd_name)
        part_package = AvdManagerCommand.CreateAvdCommandPart.AVD_PACKAGE.format(avd_schema.create_avd_package)

        if avd_schema.create_avd_device == "":
            part_device = avd_schema.avd_device
        else:
            part_device = AvdManagerCommand.CreateAvdCommandPart.AVD_DEVICE.format(avd_schema.create_avd_device)

        if avd_schema.create_avd_tag == "":
            part_tag = avd_schema.create_avd_tag
        else:
            part_tag = AvdManagerCommand.CreateAvdCommandPart.AVD_TAG.format(avd_schema.create_avd_tag)

        if avd_schema.create_avd_abi == "":
            part_abi = avd_schema.create_avd_abi
        else:
            part_abi = AvdManagerCommand.CreateAvdCommandPart.AVD_ABI.format(avd_schema.create_avd_abi)

        part_avd_additional_options = AvdManagerCommand.CreateAvdCommandPart.AVD_ADDITIONAL_OPTIONS.format(
            avd_schema.create_avd_additional_options)

        create_avd_cmd = "{} {} {} {} {} {} {} {} {}".format(part_answer_no, self.avdmanager_bin, part_create_avd,
                                                             part_name, part_package, part_device, part_tag, part_abi,
                                                             part_avd_additional_options)
        return ShellHelper.execute_shell(create_avd_cmd, True, True)


class EmulatorController:
    TAG = "EmulatorController:"

    emulator_bin = dict()

    def __init__(self):
        tools_dir = clean_path(add_ending_slash(str(GlobalConfig.SDK_DIR)) + "tools/")

        try:
            for the_file in os.listdir(tools_dir):
                file_path = os.path.join(tools_dir, the_file)
                if os.path.isfile(file_path) and "emulator" in file_path:
                    binary_name = re.findall("tools/(emulator*.+)", file_path)
                    self.emulator_bin[str(binary_name[0])] = file_path
        finally:
            if len(self.emulator_bin) == 0:
                message = "Unable to find emulator binary files in direction '{}' of Android SDK."
                message = message.format(str(tools_dir))
                raise LauncherFlowInterruptedException(self.TAG, message)

            else:
                Printer.system_message(self.TAG, "Emulator related binary files found in Android SDK:\n" + '\n'.join(
                    ["              - '" + path + "'" for path in self.emulator_bin.values()]))

    def launch_avd(self, avd_schema, port, log_file):
        part_emulator_binary = self.emulator_bin[avd_schema.launch_avd_launch_binary_name]
        part_port = EmulatorCommand.LaunchAvdCommandPart.AVD_PORT.format(port)
        part_name = EmulatorCommand.LaunchAvdCommandPart.AVD_NAME.format(avd_schema.avd_name)

        part_snapshot = ""
        if avd_schema.launch_avd_snapshot_filepath != "":
            part_snapshot = EmulatorCommand.LaunchAvdCommandPart.AVD_SNAPSHOT.format(
                avd_schema.launch_avd_snapshot_filepath)

        part_additional_options = EmulatorCommand.LaunchAvdCommandPart.AVD_ADDITIONAL_OPTIONS.format(
            avd_schema.launch_avd_additional_options)

        part_output_file = "{} {}".format(GeneralCommand.DELEGATE_OUTPUT_TO_FILE.format(log_file),
                                          GeneralCommand.CHANGE_THREAD)

        launch_avd_cmd = "{} {} {} {} {} {}".format(part_emulator_binary, part_name, part_port, part_snapshot,
                                                    part_additional_options, part_output_file)

        return ShellHelper.execute_shell(launch_avd_cmd, True, False)

    def apply_config_to_avd(self, avd_schema):
        config_ini_to_apply_filepath = clean_path(avd_schema.create_avd_hardware_config_filepath)

        real_config_ini_file_path = clean_path(
            add_ending_slash(GlobalConfig.AVD_DIR) + add_ending_slash("avd") + add_ending_slash(
                avd_schema.avd_name + ".avd") + "config.ini")

        real_config_ini_file = None
        config_ini_to_apply_file = None
        try:
            config_ini_to_apply_file = open(config_ini_to_apply_filepath, "r")
            real_config_ini_file = open(real_config_ini_file_path, "w")
            real_config_ini_file.seek(0)
            real_config_ini_file.truncate()

            for config_line in config_ini_to_apply_file.readlines():
                temp_lane = config_line
                if "AvdId=" in config_line:
                    temp_lane = ("AvdId=" + str(avd_schema.avd_name) + "\n")
                if "avd.ini.displayname=" in config_line:
                    temp_lane = ("avd.ini.displayname=" + str(avd_schema.avd_name) + "\n")
                real_config_ini_file.write(temp_lane)
        finally:
            if real_config_ini_file is not None:
                real_config_ini_file.close()
            if config_ini_to_apply_file is not None:
                config_ini_to_apply_file.close()

        return "Config.ini successfully applied"


class GradleController:
    TAG = "GradleController:"

    gradle_bin = None

    project_root_found = False
    gradlew_found = False

    def __init__(self):
        self.gradle_bin = GlobalConfig.PROJECT_ROOT_DIR + "gradlew"

        self.project_root_found = GlobalConfig.PROJECT_ROOT_DIR != "" and os.path.isdir(GlobalConfig.PROJECT_ROOT_DIR)
        self.gradlew_found = os.path.isfile(self.gradle_bin)

        if self.project_root_found:
            Printer.system_message(self.TAG,
                                   "Project root dir '" + GlobalConfig.PROJECT_ROOT_DIR + "' was found! Building new .*apk is possible.")
            if self.gradlew_found:
                Printer.system_message(self.TAG, "gradlew binary found at'" + str(self.gradle_bin) + "'.")

    def build_application_apk(self, test_set):
        application_apk_assemble_task = test_set.application_apk_assemble_task
        self._check_if_build_is_possible(application_apk_assemble_task)

        cmd = GradleCommand.RUN_TASK_IN_OTHER_DIRECTORY.format(self.gradle_bin, GlobalConfig.PROJECT_ROOT_DIR,
                                                               application_apk_assemble_task)
        ShellHelper.execute_shell(cmd, True, True)

    def build_test_apk(self, test_set):
        test_apk_assemble_task = test_set.test_apk_assemble_task
        self._check_if_build_is_possible(test_apk_assemble_task)

        cmd = GradleCommand.RUN_TASK_IN_OTHER_DIRECTORY.format(self.gradle_bin, GlobalConfig.PROJECT_ROOT_DIR,
                                                               test_apk_assemble_task)
        ShellHelper.execute_shell(cmd, True, True)

    def _check_if_build_is_possible(self, cmd):
        if cmd == "":
            message = "Gradle assemble task (for building .*apk) was not specified in TestManifest. Launcher will quit."
            raise LauncherFlowInterruptedException(self.TAG, message)

        if not self.project_root_found:
            message = "Unable to build new .*apk. Project root not found. Launcher will quit."
            raise LauncherFlowInterruptedException(self.TAG, message)

        if not self.gradlew_found:
            message = "Unable to build new .*apk. File 'gradlew' not found in dir '{}'. Launcher will quit."
            message = message.format(GlobalConfig.PROJECT_ROOT_DIR)
            raise LauncherFlowInterruptedException(self.TAG, message)


class InstrumentationRunnerController:
    TAG = "InstrumentationRunnerController:"

    adb_bin = None

    def __init__(self):
        self.adb_bin = clean_path(add_ending_slash(GlobalConfig.SDK_DIR) + "platform-tools/adb")

        if os.path.isfile(self.adb_bin):
            Printer.system_message(self.TAG, "ADB binary file found at '" + self.adb_bin + "'.")
        else:
            message = "Unable to find ADB binary at '{}'."
            message = message.format(self.adb_bin)
            raise LauncherFlowInterruptedException(self.TAG, message)

    def assemble_run_test_package_cmd(self, device_adb_name, test_package):
        return InstrumentationRunnerCommand.RUN_TEST_PACKAGE.format(self.adb_bin,
                                                                    AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                                                    test_package, GlobalConfig.INSTRUMENTATION_RUNNER)
