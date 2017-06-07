import os
import re

from error.Exceptions import LauncherFlowInterruptedException

from settings import GlobalConfig

from system.bin.AndroidShellCommandAssemblers import (
    AaptCommandAssembler,
    AdbCommandAssembler,
    AdbShellCommandAssembler,
    AdbPackageManagerCommandAssembler,
    AdbSettingsCommandAssembler,
    AdbLogCatCommandAssembler,
    AvdManagerCommandAssembler,
    EmulatorCommandAssembler,
    GradleCommandAssembler,
    InstrumentationRunnerCommandAssembler

)
from system.console import (
    Printer,
    ShellHelper,
    Color
)
from system.file.FileUtils import (
    clean_path,
    add_ending_slash
)


class AaptController:
    TAG = "AaptController:"

    aapt_bin = None

    def __init__(self):
        build_tools = self._find_latest_build_tools()
        self.aapt_bin = clean_path(add_ending_slash(GlobalConfig.SDK_DIR) + "build-tools/" + build_tools + "/aapt")
        self._assert_bin_directory_exists()
        self.aapt_command_assembler = AaptCommandAssembler()

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
            Printer.system_message(self.TAG, "Android SDK Build-Tools with latest version were selected: "
                                   + Color.GREEN + str(build_tools_folder_with_highest_ver) + Color.BLUE + ".")
        return build_tools_folder_with_highest_ver

    def _assert_bin_directory_exists(self):
        if os.path.isfile(self.aapt_bin):
            Printer.system_message(self.TAG, "Aapt binary file found at: " + Color.GREEN + self.aapt_bin
                                   + Color.BLUE + ".")
        else:
            message = "Unable to find Aapt binary at '{}'."
            message = message.format(self.aapt_bin)
            raise LauncherFlowInterruptedException(self.TAG, message)

    def dump_badging(self, apk_filepath):
        cmd = self.aapt_command_assembler.assemble_dump_badging_cmd(self.aapt_bin, apk_filepath)
        return ShellHelper.execute_shell(cmd, False, False)

    def list_resources(self, apk_filepath):
        cmd = self.aapt_command_assembler.assemble_list_all_cmd(self.aapt_bin, apk_filepath)
        return ShellHelper.execute_shell(cmd, False, False)


class AdbController:
    TAG = "AdbController:"

    adb_bin = None

    def __init__(self):
        self.adb_bin = clean_path(add_ending_slash(GlobalConfig.SDK_DIR) + "platform-tools/adb")
        self._assert_bin_directory_exists()
        self.adb_command_assembler = AdbCommandAssembler()

    def _assert_bin_directory_exists(self):
        if os.path.isfile(self.adb_bin):
            Printer.system_message(self.TAG, "ADB binary file found at " + Color.GREEN + self.adb_bin + Color.BLUE
                                   + ".")
        else:
            message = "Unable to find ADB binary at '{}'."
            message = message.format(self.adb_bin)
            raise LauncherFlowInterruptedException(self.TAG, message)

    def start_server(self):
        cmd = self.adb_command_assembler.assemble_start_server_cmd(self.adb_bin)
        return ShellHelper.execute_shell(cmd, True, True)

    def kill_server(self):
        cmd = self.adb_command_assembler.assemble_kill_server_cmd(self.adb_bin)
        return ShellHelper.execute_shell(cmd, True, True)

    def devices(self):
        cmd = self.adb_command_assembler.assemble_devices_cmd(self.adb_bin)
        return ShellHelper.execute_shell(cmd, False, False)

    def wait_for_device(self):
        cmd = self.adb_command_assembler.assemble_wait_for_device_cmd(self.adb_bin)
        return ShellHelper.execute_shell(cmd, False, False)

    def kill_device(self, device_adb_name):
        cmd = self.adb_command_assembler.assemble_kill_device_cmd(self.adb_bin, device_adb_name)
        return ShellHelper.execute_shell(cmd, True, False)

    def install_apk(self, device_adb_name, apk_name):
        cmd = self.adb_command_assembler.assemble_install_apk_cmd(self.adb_bin, device_adb_name, apk_name)
        return ShellHelper.execute_shell(cmd, True, False)

    def pull(self, device_adb_name, file_dir, file_destination):
        cmd = self.adb_command_assembler.assemble_pull_file_cmd(self.adb_bin,
                                                                device_adb_name,
                                                                file_dir,
                                                                file_destination)
        return ShellHelper.execute_shell(cmd, False, False)


class AdbShellController:
    TAG = "AdbShellController:"

    adb_bin = None

    def __init__(self):
        self.adb_bin = clean_path(add_ending_slash(GlobalConfig.SDK_DIR) + "platform-tools/adb")
        self._assert_bin_directory_exists()
        self.adb_shell_command_assembler = AdbShellCommandAssembler()

    def _assert_bin_directory_exists(self):
        if os.path.isfile(self.adb_bin):
            Printer.system_message(self.TAG, "ADB binary file found at " + Color.GREEN + self.adb_bin + Color.BLUE
                                   + ".")
        else:
            message = "Unable to find ADB binary at '{}'."
            message = message.format(self.adb_bin)
            raise LauncherFlowInterruptedException(self.TAG, message)

    def get_property(self, device_adb_name, device_property):
        cmd = self.adb_shell_command_assembler.assemble_get_property_cmd(self.adb_bin, device_adb_name, device_property)
        return ShellHelper.execute_shell(cmd, False, False)

    def record_screen(self, device_adb_name, file_dir):
        cmd = self.adb_shell_command_assembler.assemble_record_screen_cmd(self.adb_bin, device_adb_name, file_dir)
        return ShellHelper.execute_shell(cmd, False, False)

    def remove_file(self, device_adb_name, file_dir):
        cmd = self.adb_shell_command_assembler.assemble_remove_file_cmd(self.adb_bin, device_adb_name, file_dir)
        return ShellHelper.execute_shell(cmd, True, True)

    def remove_files_in_dir(self, device_adb_name, file_dir):
        cmd = self.adb_shell_command_assembler.assemble_remove_files_in_dir_cmd(self.adb_bin, device_adb_name, file_dir)
        return ShellHelper.execute_shell(cmd, True, True)

    def create_dir(self, device_adb_name, file_dir):
        cmd = self.adb_shell_command_assembler.assemble_create_dir_cmd(self.adb_bin, device_adb_name, file_dir)
        return ShellHelper.execute_shell(cmd, True, True)


class AdbPackageManagerController:
    TAG = "AdbPackageManagerController:"

    adb_bin = None

    def __init__(self):
        self.adb_bin = clean_path(add_ending_slash(GlobalConfig.SDK_DIR) + "platform-tools/adb")
        self._assert_bin_directory_exists()
        self.adb_package_manager_command_assembler = AdbPackageManagerCommandAssembler()

    def _assert_bin_directory_exists(self):
        if os.path.isfile(self.adb_bin):
            Printer.system_message(self.TAG, "ADB binary file found at " + Color.GREEN + self.adb_bin + Color.BLUE
                                   + ".")
        else:
            message = "Unable to find ADB binary at '{}'."
            message = message.format(self.adb_bin)
            raise LauncherFlowInterruptedException(self.TAG, message)

    def get_installed_packages(self, device_adb_name):
        cmd = self.adb_package_manager_command_assembler.assemble_list_installed_packages_cmd(self.adb_bin,
                                                                                              device_adb_name)
        return ShellHelper.execute_shell(cmd, False, False)

    def uninstall_package(self, device_adb_name, package_name):
        cmd = self.adb_package_manager_command_assembler.assemble_uninstall_package_cmd(self.adb_bin,
                                                                                        device_adb_name,
                                                                                        package_name)
        return ShellHelper.execute_shell(cmd, True, True)


class AdbSettingsController:
    TAG = "AdbSettingsController:"

    adb_bin = None

    def __init__(self):
        self.adb_bin = clean_path(add_ending_slash(GlobalConfig.SDK_DIR) + "platform-tools/adb")
        self._assert_bin_directory_exists()
        self.adb_settings_command_assembler = AdbSettingsCommandAssembler()

    def _assert_bin_directory_exists(self):
        if os.path.isfile(self.adb_bin):
            Printer.system_message(self.TAG, "ADB binary file found at " + Color.GREEN + self.adb_bin + Color.BLUE
                                   + ".")
        else:
            message = "Unable to find ADB binary at '{}'."
            message = message.format(self.adb_bin)
            raise LauncherFlowInterruptedException(self.TAG, message)

    def get_device_android_id(self, device_adb_name):
        cmd = self.adb_settings_command_assembler.assemble_get_device_android_id_cmd(self.adb_bin,
                                                                                     device_adb_name)
        return ShellHelper.execute_shell(cmd, False, False)


class AdbLogCatController:
    TAG = "AdbLogCatController:"

    def __init__(self):
        self.adb_bin = clean_path(add_ending_slash(GlobalConfig.SDK_DIR) + "platform-tools/adb")
        self._assert_bin_directory_exists()
        self.adb_logcat_command_assembler = AdbLogCatCommandAssembler()

    def _assert_bin_directory_exists(self):
        if os.path.isfile(self.adb_bin):
            Printer.system_message(self.TAG, "ADB binary file found at " + Color.GREEN + self.adb_bin + Color.BLUE
                                   + ".")
        else:
            message = "Unable to find ADB binary at '{}'."
            message = message.format(self.adb_bin)
            raise LauncherFlowInterruptedException(self.TAG, message)

    def flush_logcat(self, device_adb_name):
        cmd = self.adb_logcat_command_assembler.assemble_flush_logcat_cmd(self.adb_bin, device_adb_name)

        return ShellHelper.execute_shell(cmd, False, False)

    def read_logcat(self, device_adb_name):
        cmd = self.adb_logcat_command_assembler.assemble_dump_logcat_cmd(self.adb_bin, device_adb_name)

        return ShellHelper.execute_shell(cmd, False, False)

    def monitor_logcat(self, device_adb_name):
        cmd = self.adb_logcat_command_assembler.monitor_logcat_schema(self.adb_bin, device_adb_name)

        return ShellHelper.execute_shell(cmd, False, False)


class AvdManagerController:
    TAG = "AvdManagerController:"

    avdmanager_bin = None

    def __init__(self):
        self.avdmanager_bin = clean_path(add_ending_slash(GlobalConfig.SDK_DIR) + "tools/bin/avdmanager")
        self._assert_bin_directory_exists()
        self.avdmanager_command_assembler = AvdManagerCommandAssembler()

    def _assert_bin_directory_exists(self):
        if os.path.isfile(self.avdmanager_bin):
            Printer.system_message(self.TAG, "AvdManager binary file found at " + Color.GREEN + self.avdmanager_bin
                                   + Color.BLUE + ".")
        else:
            message = "Unable to find ADB binary at '{}'."
            message = message.format(self.avdmanager_bin)
            raise LauncherFlowInterruptedException(self.TAG, message)

    def list_avd(self):
        cmd = self.avdmanager_command_assembler.assemble_list_avd_cmd(self.avdmanager_bin)
        return ShellHelper.execute_shell(cmd, False, False)

    def delete_avd(self, avd_schema):
        cmd = self.avdmanager_command_assembler.assemble_delete_avd_cmd(self.avdmanager_bin, avd_schema)
        return ShellHelper.execute_shell(cmd, True, True)

    def create_avd(self, avd_schema):
        cmd = self.avdmanager_command_assembler.assemble_create_avd_cmd(self.avdmanager_bin, avd_schema)
        return ShellHelper.execute_shell(cmd, True, True)


class EmulatorController:
    TAG = "EmulatorController:"

    emulator_bin_dict = dict()

    def __init__(self):
        self.emulator_bin_dict = self._display_emulator_binaries()
        self.emulator_command_assembler = EmulatorCommandAssembler()

    def _display_emulator_binaries(self):
        emulator_binaries = dict()

        emulator_dir = clean_path(add_ending_slash(str(GlobalConfig.SDK_DIR)) + "emulator/")
        try:
            for the_file in os.listdir(emulator_dir):
                file_path = os.path.join(emulator_dir, the_file)
                if os.path.isfile(file_path) and "emulator" in file_path:
                    binary_name = re.findall("emulator\/(emulator*.+)", file_path)

                    if binary_name:
                        emulator_binaries[str(binary_name[0])] = file_path
        finally:
            if len(emulator_binaries) == 0:
                message = "Unable to find emulator binary files in direction '{}' of Android SDK."
                message = message.format(str(emulator_dir))
                raise LauncherFlowInterruptedException(self.TAG, message)

            else:
                Printer.system_message(self.TAG, "Emulator related binary files found in Android SDK:")
                for path in emulator_binaries.values():
                    Printer.system_message(self.TAG, "  * " + Color.GREEN + path + Color.BLUE)

        return emulator_binaries

    def launch_avd(self, avd_schema, port, log_file):
        emulator_binary = self.emulator_bin_dict[avd_schema.launch_avd_launch_binary_name]
        cmd = self.emulator_command_assembler.assemble_launch_avd_cmd(emulator_binary, avd_schema, port, log_file)
        return ShellHelper.execute_shell(cmd, True, False)

    @staticmethod
    def apply_config_to_avd(avd_schema):
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
        self._check_if_gradle_binary_was_found()
        self.gradle_command_assembler = GradleCommandAssembler()

    def _check_if_gradle_binary_was_found(self):
        self.project_root_found = GlobalConfig.PROJECT_ROOT_DIR != "" and os.path.isdir(GlobalConfig.PROJECT_ROOT_DIR)
        self.gradlew_found = os.path.isfile(self.gradle_bin)
        if self.project_root_found:
            Printer.system_message(self.TAG, "Project root dir " + Color.GREEN + GlobalConfig.PROJECT_ROOT_DIR
                                   + Color.BLUE + " was found! Building new .*apk is possible.")
            if self.gradlew_found:
                Printer.system_message(self.TAG, "gradlew binary found at " + Color.GREEN + str(self.gradle_bin)
                                       + Color.BLUE + ".")

    def build_application_apk(self, test_set):
        assemble_task = test_set.application_apk_assemble_task
        self._check_if_build_is_possible(assemble_task)

        cmd = self.gradle_command_assembler.assemble_build_application_apk_cmd(self.gradle_bin,
                                                                               test_set.gradle_build_params,
                                                                               assemble_task,
                                                                               GlobalConfig.PROJECT_ROOT_DIR)
        ShellHelper.execute_shell(cmd, True, True)

    def build_test_apk(self, test_set):
        assemble_task = test_set.test_apk_assemble_task
        self._check_if_build_is_possible(assemble_task)

        cmd = self.gradle_command_assembler.assemble_build_test_apk_cmd(self.gradle_bin,
                                                                        test_set.gradle_build_params,
                                                                        assemble_task,
                                                                        GlobalConfig.PROJECT_ROOT_DIR)
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
        self._assert_bin_directory_exists()
        self.instrumentation_runner_command_assembler = InstrumentationRunnerCommandAssembler()

    def _assert_bin_directory_exists(self):
        if os.path.isfile(self.adb_bin):
            Printer.system_message(self.TAG, "ADB binary file found at " + Color.GREEN + self.adb_bin + Color.BLUE
                                   + ".")
        else:
            message = "Unable to find ADB binary at '{}'."
            message = message.format(self.adb_bin)
            raise LauncherFlowInterruptedException(self.TAG, message)
