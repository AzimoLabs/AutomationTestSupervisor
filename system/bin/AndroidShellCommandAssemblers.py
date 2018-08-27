from system.bin.AndroidShellCommands import (
    AaptCommand,
    AdbCommand,
    AdbShellCommand,
    AdbActivityManagerCommand,
    AdbPackageManagerCommand,
    AdbSettingsCommand,
    AdbLogCatCommand,
    AvdManagerCommand,
    EmulatorCommand,
    GradleCommand,
    InstrumentationRunnerCommand
)
from system.bin.SystemShellCommands import GeneralCommand


class AaptCommandAssembler:
    dump_badging_schema = "{} {}"
    list_all_schema = "{} {}"

    def assemble_dump_badging_cmd(self, aapt_bin, apk_filepath):
        return self.dump_badging_schema.format(aapt_bin,
                                               AaptCommand.DUMP_BADGING.format(apk_filepath))

    def assemble_list_all_cmd(self, aapt_bin, apk_filepath):
        return self.list_all_schema.format(aapt_bin,
                                           AaptCommand.LIST_ALL.format(apk_filepath))


class AdbCommandAssembler:
    start_server_schema = "{} {}"
    kill_server_schema = "{} {}"
    devices_schema = "{} {}"
    waif_for_device_schema = "{} {}"
    kill_device_schema = "{} {} {}"
    install_apk_schema = "{} {} {} {}"
    pull_file_schema = "{} {} {}"

    def assemble_start_server_cmd(self, adb_bin):
        return self.start_server_schema.format(adb_bin,
                                               AdbCommand.START_SERVER)

    def assemble_kill_server_cmd(self, adb_bin):
        return self.kill_server_schema.format(adb_bin,
                                              AdbCommand.KILL_SERVER)

    def assemble_devices_cmd(self, adb_bin):
        return self.devices_schema.format(adb_bin,
                                          AdbCommand.DEVICES)

    def assemble_wait_for_device_cmd(self, adb_bin):
        return self.waif_for_device_schema.format(adb_bin,
                                                  AdbCommand.WAIT_FOR_DEVICE)

    def assemble_kill_device_cmd(self, adb_bin, device_adb_name):
        return self.kill_device_schema.format(adb_bin,
                                              AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                              AdbCommand.KILL_DEVICE)

    def assemble_install_apk_cmd(self, adb_bin, device_adb_name, apk_name):
        return self.install_apk_schema.format(adb_bin,
                                              AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                              AdbCommand.INSTALL_APK.format(apk_name),
                                              GeneralCommand.CHANGE_THREAD)

    def assemble_pull_file_cmd(self, adb_bin, device_adb_name, file_dir, file_destination_dir):
        return self.pull_file_schema.format(adb_bin,
                                            AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                            AdbCommand.PULL.format(file_dir, file_destination_dir))


class AdbShellCommandAssembler:
    get_property_schema = "{} {} {} {}"
    record_screen = "{} {} {} {}"
    remove_file = "{} {} {} {}"
    remove_files_in_dir = "{} {} {} {}"
    create_dir = "{} {} {} {}"
    check_if_dir_exists = "{} {} {} {}"

    def assemble_get_property_cmd(self, adb_bin, device_adb_name, device_property):
        return self.get_property_schema.format(adb_bin,
                                               AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                               AdbShellCommand.SHELL,
                                               AdbShellCommand.GET_PROPERTY.format(device_property))

    def assemble_record_screen_cmd(self, adb_bin, device_adb_name, file_dir):
        return self.record_screen.format(adb_bin,
                                         AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                         AdbShellCommand.SHELL,
                                         AdbShellCommand.RECORD.format(file_dir))

    def assemble_remove_file_cmd(self, adb_bin, device_adb_name, file_dir):
        return self.remove_file.format(adb_bin,
                                       AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                       AdbShellCommand.SHELL,
                                       AdbShellCommand.REMOVE_FILE.format(file_dir))

    def assemble_remove_files_in_dir_cmd(self, adb_bin, device_adb_name, file_dir):
        return self.remove_files_in_dir.format(adb_bin,
                                               AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                               AdbShellCommand.SHELL,
                                               AdbShellCommand.REMOVE_FILES_IN_DIR.format(file_dir))

    def assemble_create_dir_cmd(self, adb_bin, device_adb_name, file_dir):
        return self.create_dir.format(adb_bin,
                                      AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                      AdbShellCommand.SHELL,
                                      AdbShellCommand.CREATE_DIR.format(file_dir))

    def assemble_check_if_dir_exists_cmd(self, adb_bin, device_adb_name, directory):
        return self.check_if_dir_exists.format(adb_bin,
                                               AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                               AdbShellCommand.SHELL,
                                               GeneralCommand.CHECK_IF_DIR_EXISTS.format(directory))


class AdbPackageManagerCommandAssembler:
    list_installed_packages_schema = "{} {} {} {} {}"
    uninstall_package_schema = "{} {} {} {} {}"
    clear_package_cache_schema = "{} {} {} {} {}"

    def assemble_list_installed_packages_cmd(self, adb_bin, device_adb_name):
        return self.list_installed_packages_schema.format(adb_bin,
                                                          AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                                          AdbShellCommand.SHELL,
                                                          AdbPackageManagerCommand.PACKAGE_MANAGER,
                                                          AdbPackageManagerCommand.LIST_SERVICES)

    def assemble_uninstall_package_cmd(self, adb_bin, device_adb_name, package_name):
        return self.uninstall_package_schema.format(adb_bin,
                                                    AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                                    AdbShellCommand.SHELL,
                                                    AdbPackageManagerCommand.PACKAGE_MANAGER,
                                                    AdbPackageManagerCommand.UNINSTALL_PACKAGE.format(package_name))

    def assemble_clear_package_cache_cmd(self, adb_bin, device_adb_name, package_name):
        return self.clear_package_cache_schema.format(adb_bin,
                                                      AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                                      AdbShellCommand.SHELL,
                                                      AdbPackageManagerCommand.PACKAGE_MANAGER,
                                                      AdbPackageManagerCommand.CLEAR_CACHE.format(package_name))


class AdbSettingsCommandAssembler:
    get_device_android_id_schema = "{} {} {} {} {}"

    def assemble_get_device_android_id_cmd(self, adb_bin, device_adb_name):
        return self.get_device_android_id_schema.format(adb_bin,
                                                        AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                                        AdbShellCommand.SHELL,
                                                        AdbSettingsCommand.SETTINGS,
                                                        AdbSettingsCommand.GET_DEVICE_ANDROID_ID)


class AdbLogCatCommandAssembler:
    flush_logcat_schema = "{} {} {} {}"
    dump_logcat_schema = "{} {} {} {}"
    monitor_logcat_schema = "{} {} {}"

    def assemble_monitor_logcat_cmd(self, adb_bin, device_adb_name):
        return self.monitor_logcat_schema.format(adb_bin,
                                                 AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                                 AdbLogCatCommand.LOG_CAT)

    def assemble_flush_logcat_cmd(self, adb_bin, device_adb_name):
        return self.flush_logcat_schema.format(adb_bin,
                                               AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                               AdbLogCatCommand.LOG_CAT,
                                               AdbLogCatCommand.FLUSH)

    def assemble_dump_logcat_cmd(self, adb_bin, device_adb_name):
        return self.dump_logcat_schema.format(adb_bin,
                                              AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                              AdbLogCatCommand.LOG_CAT,
                                              AdbLogCatCommand.DUMP)


class AvdManagerCommandAssembler:
    list_avd_schema = "{} {}"
    delete_avd_schema = "{} {}"
    create_avd_schema = "{} {} {} {} {} {} {} {} {}"

    def assemble_list_avd_cmd(self, avdmanager_bin):
        return self.list_avd_schema.format(avdmanager_bin,
                                           AvdManagerCommand.LIST_AVD)

    def assemble_delete_avd_cmd(self, avdmanager_bin, avd_schema):
        return self.delete_avd_schema.format(avdmanager_bin,
                                             AvdManagerCommand.DELETE_AVD.format(avd_schema.avd_name))

    def assemble_create_avd_cmd(self, avdmanager_bin, avd_schema):
        part_answer_no = GeneralCommand.ANSWER_NO
        part_create_avd = AvdManagerCommand.CreateAvdCommandPart.AVD_CREATE
        part_name = AvdManagerCommand.CreateAvdCommandPart.AVD_NAME.format(avd_schema.avd_name)
        part_package = AvdManagerCommand.CreateAvdCommandPart.AVD_PACKAGE.format(avd_schema.create_avd_package)

        if avd_schema.create_avd_device == "":
            part_device = avd_schema.create_avd_device
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

        return self.create_avd_schema.format(part_answer_no,
                                             avdmanager_bin,
                                             part_create_avd,
                                             part_name,
                                             part_package,
                                             part_device,
                                             part_tag,
                                             part_abi,
                                             part_avd_additional_options)


class EmulatorCommandAssembler:
    launch_avd_schema = "{} {} {} {} {} {}"
    output_file_schema = "{} {}"

    def assemble_launch_avd_cmd(self, emulator_bin, avd_schema, port, log_file):
        part_emulator_binary = emulator_bin
        part_port = EmulatorCommand.LaunchAvdCommandPart.AVD_PORT.format(port)
        part_name = EmulatorCommand.LaunchAvdCommandPart.AVD_NAME.format(avd_schema.avd_name)

        part_snapshot = ""
        if avd_schema.launch_avd_snapshot_filepath != "":
            part_snapshot = EmulatorCommand.LaunchAvdCommandPart.AVD_SNAPSHOT.format(
                avd_schema.launch_avd_snapshot_filepath)

        part_additional_options = EmulatorCommand.LaunchAvdCommandPart.AVD_ADDITIONAL_OPTIONS.format(
            avd_schema.launch_avd_additional_options)

        part_output_file = self.output_file_schema.format(GeneralCommand.DELEGATE_OUTPUT_TO_FILE.format(log_file),
                                                          GeneralCommand.CHANGE_THREAD)

        return self.launch_avd_schema.format(part_emulator_binary,
                                             part_name,
                                             part_port,
                                             part_snapshot,
                                             part_additional_options,
                                             part_output_file)


class GradleCommandAssembler:
    gradle_command_schema = "{} {}"

    def assemble_build_application_apk_cmd(self, gradle_bin, gradle_params, assemble_task, project_root_dir):
        gradle_cmd = GradleCommand.RUN_TASK_IN_OTHER_DIRECTORY.format(gradle_bin,
                                                                      project_root_dir,
                                                                      assemble_task)
        return self.gradle_command_schema.format(gradle_cmd, gradle_params)

    def assemble_build_test_apk_cmd(self, gradle_bin, gradle_params, assemble_task, project_root_dir):
        gradle_cmd = GradleCommand.RUN_TASK_IN_OTHER_DIRECTORY.format(gradle_bin,
                                                                      project_root_dir,
                                                                      assemble_task)
        return self.gradle_command_schema.format(gradle_cmd, gradle_params)


class InstrumentationRunnerCommandAssembler:
    test_command_schema = "{} {} {} {} {} {} {} {}"
    single_test_command_schema = "{} {} {} {} {} {} {}{} {}"

    def assemble_run_test_package_cmd(self, adb_binary, device_adb_name, params, instrumentation_runner):
        parameters = self._assemble_params(params)
        return self.test_command_schema.format(adb_binary,
                                               AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                               AdbShellCommand.SHELL,
                                               AdbActivityManagerCommand.ACTIVITY_MANAGER,
                                               InstrumentationRunnerCommand.INSTRUMENT_PROCESS,
                                               InstrumentationRunnerCommand.DISPLAY_RAW_MESSAGE,
                                               parameters,
                                               InstrumentationRunnerCommand.INSTRUMENTATION_RUNNER.format(
                                                   instrumentation_runner)
                                               )

    def assemble_run_single_test_cmd(self, adb_binary, device_adb_name, test_class, test_name, instrumentation_runner):
        return self.single_test_command_schema.format(adb_binary,
                                                      AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                                      AdbShellCommand.SHELL,
                                                      AdbActivityManagerCommand.ACTIVITY_MANAGER,
                                                      InstrumentationRunnerCommand.INSTRUMENT_PROCESS,
                                                      InstrumentationRunnerCommand.DISPLAY_RAW_MESSAGE,
                                                      InstrumentationRunnerCommand.CLASS.format(test_class),
                                                      InstrumentationRunnerCommand.TEST_CASE.format(test_name),
                                                      InstrumentationRunnerCommand.INSTRUMENTATION_RUNNER.format(
                                                          instrumentation_runner)
                                                      )

    @staticmethod
    def _assemble_params(params):
        parameters = ""
        for param, value in params.items():
            if param == "package":
                parameters += (" " + InstrumentationRunnerCommand.PACKAGE.format(value))
            if param == "numShards":
                parameters += (" " + InstrumentationRunnerCommand.NUM_SHARD.format(value))
            if param == "shardIndex":
                parameters += (" " + InstrumentationRunnerCommand.SHARD_INDEX.format(value))
        return parameters
