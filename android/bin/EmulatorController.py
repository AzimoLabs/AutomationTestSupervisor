from android.bin.command.EmulatorCommand import *
from system.command.GeneralCommand import *
from system.mapper.PathMapper import *
from system.manager.FileManager import *
from console.ShellHelper import *
from console.Printer import *
from settings.Settings import *
import re

TAG = "EmulatorController:"


class EmulatorController:
    emulator_bin = dict()

    def __init__(self):
        tools_dir = clean_path(
            add_ending_slash(str(Settings.SDK_DIR)) + "tools/")

        try:
            for the_file in os.listdir(tools_dir):
                file_path = os.path.join(tools_dir, the_file)
                if os.path.isfile(file_path) and "emulator" in file_path:
                    binary_name = re.findall("tools/(emulator*.+)", file_path)
                    self.emulator_bin[str(binary_name[0])] = file_path
        finally:
            if len(self.emulator_bin) == 0:
                print_error(TAG,
                            "Unable to find emulator binary files in direction '" + str(
                                tools_dir) + "' of Android SDK.")
                quit()
            else:
                print_message(TAG, "Emulator related binary files found in Android SDK:\n" + '\n'.join(
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
        launch_avd_cmd = "{} {} {} {} {} {}".format(part_emulator_binary,
                                                    part_name,
                                                    part_port,
                                                    part_snapshot,
                                                    part_additional_options,
                                                    part_output_file)

        return execute_shell(launch_avd_cmd, True, False)

    def apply_config_to_avd(self, avd_schema):
        config_ini_file_path = clean_path(avd_schema.create_avd_hardware_config_filepath)
        temp_file_path = config_ini_file_path.replace(".ini", "_temp.ini", 1)

        temp_file = None
        config_ini_file = None
        try:
            config_ini_file = open(config_ini_file_path, "r")
            temp_file = open(temp_file_path, "w")

            for config_line in config_ini_file.readlines():
                temp_lane = config_line
                if "AvdId=" in config_line:
                    temp_lane = ("AvdId=" + str(avd_schema.avd_name) + "\n")
                if "avd.ini.displayname=" in config_line:
                    temp_lane = ("avd.ini.displayname=" + str(avd_schema.avd_name) + "\n")
                temp_file.write(temp_lane)
        finally:
            if temp_file is not None:
                temp_file.close()
            if config_ini_file is not None:
                config_ini_file.close()

        config_ini_location = clean_path(
            add_ending_slash(Settings.AVD_DIR) +
            add_ending_slash("avd") +
            add_ending_slash(avd_schema.avd_name + ".avd") +
            "config.ini")

        output = execute_shell(GeneralCommand.COPY_FROM_TO.format(
            temp_file_path,
            config_ini_location),
            True, False)

        delete_file(temp_file_path)
        return output
