import os

from settings.manifest.path.PathManifestModels import PathManifest
from settings.manifest.launch.LaunchManifestModels import LaunchManifest
from settings.manifest.avd.AvdManifestModels import AvdManifest
from settings.manifest.test.TestManifestModels import TestManifest
from settings.loader import ArgLoader
from settings import GlobalConfig

from system.console import Printer
from system.file.FileUtils import (
    clean_path,
    add_ending_slash
)

TAG = "SettingsLoader:"

ANDROID_HOME_ENV = os.getenv('ANDROID_HOME')
ANDROID_SDK_HOME_ENV = os.getenv('ANDROID_SDK_HOME')

OUTPUT_DIR_DEFAULT = "output"


# TODO DIVIDE INTO 4 OBJECT EXTENDING BASE OBJECT WITH LOAD METHOD

def init_paths():
    path_set_name = ArgLoader.load_path_set()
    if path_set_name is None:
        Printer.error(TAG, "No path set was selected. Launcher will quit.")
        quit()
    else:
        Printer.message_highlighted(TAG, "Selected path set: ", path_set_name)

    path_manifest_dir = ArgLoader.load_path_manifest_dir()
    path_manifest = PathManifest(path_manifest_dir)
    Printer.message_highlighted(TAG, "Created PathManifest from file: ", str(path_manifest_dir))

    if path_manifest.contains_set(path_set_name):
        Printer.system_message(TAG, "Path set '" + path_set_name + "' was found in PathManifest.")
    else:
        Printer.error(TAG, "Invalid path set with name '"
                      + path_set_name + "' does not exist in PathManifest!")
        quit()

    path_set = path_manifest.get_set(path_set_name)

    GlobalConfig.SDK_DIR = add_ending_slash(clean_path((path_set.paths["sdk_dir"]).path_value))
    if GlobalConfig.SDK_DIR == "":
        Printer.system_message(TAG, "SDK path not set in PathManifest. "
                                    "Will use path set in env variable 'ANDROID_HOME'.")
        if ANDROID_HOME_ENV is None:
            Printer.error(TAG, "Env variable 'ANDROID_HOME' is not set. Launcher will quit.")
            quit()
        else:
            GlobalConfig.SDK_DIR = add_ending_slash(clean_path(ANDROID_HOME_ENV))
    Printer.message_highlighted(TAG, "Launcher will look for SDK at dir: ", GlobalConfig.SDK_DIR)

    GlobalConfig.AVD_DIR = add_ending_slash(clean_path((path_set.paths["avd_dir"]).path_value))
    if GlobalConfig.AVD_DIR == "":
        Printer.system_message(TAG, "AVD path not set in PathManifest. "
                                    "Will use path set in env variable 'ANDROID_SDK_HOME'.")
        if ANDROID_SDK_HOME_ENV is None:
            Printer.system_message(TAG, "Env variable 'ANDROID_SDK_HOME' is not set. "
                                        "Trying to recreate default path from user root.")
            GlobalConfig.AVD_DIR = add_ending_slash(clean_path("~")) + ".android"
    Printer.message_highlighted(TAG, "Launcher will look for AVD images at dir: ", GlobalConfig.AVD_DIR)

    GlobalConfig.OUTPUT_DIR = add_ending_slash(clean_path((path_set.paths["output_dir"]).path_value))
    if GlobalConfig.OUTPUT_DIR == "":
        Printer.system_message(TAG, "Output path not set in PathManifest. Default value will be used.")
        GlobalConfig.OUTPUT_DIR = OUTPUT_DIR_DEFAULT
    Printer.message_highlighted(TAG, "Launcher will generate log from tests in dir: ", GlobalConfig.OUTPUT_DIR)

    GlobalConfig.PROJECT_ROOT_DIR = add_ending_slash(clean_path((path_set.paths["project_root_dir"]).path_value))
    if GlobalConfig.PROJECT_ROOT_DIR == "":
        Printer.system_message(TAG, "Project root was not specified. This field is not obligatory.")
        Printer.error(TAG, "Warning: Without project root directory launcher will quit if no "
                           ".*apk files will be found in directory lodaded from 'apk_dir' field of PathManifest.")
    else:
        Printer.message_highlighted(TAG, "Project root dir: ", GlobalConfig.PROJECT_ROOT_DIR)

    GlobalConfig.APK_DIR = add_ending_slash(clean_path((path_set.paths["apk_dir"]).path_value))
    if GlobalConfig.APK_DIR == "":
        Printer.error(TAG, "Directory with .*apk files was not found. Launcher will quit.")
        quit()
    Printer.message_highlighted(TAG, "Launcher will look for .*apk files in dir: ", GlobalConfig.APK_DIR)


def init_launch_plan():
    launch_plan_name = ArgLoader.load_launch_plan()
    if launch_plan_name is None:
        Printer.error(TAG, "No launch plan selected. Launcher will quit.")
        quit()
    else:
        Printer.message_highlighted(TAG, "Selected launch plan: ", launch_plan_name)

    launch_manifest_dir = ArgLoader.load_launch_manifest_dir()
    launch_manifest = LaunchManifest(launch_manifest_dir)
    Printer.message_highlighted(TAG, "Created LaunchManifest from file: ", str(launch_manifest_dir))

    if launch_manifest.contains_plan(launch_plan_name):
        Printer.system_message(TAG, "Launch plan '" + launch_plan_name + "' was found in LaunchManifest.")
    else:
        Printer.error(TAG, "Invalid launch plan with name '"
                      + launch_plan_name + "' does not exist in LaunchManifest!")
        quit()

    launch_plan = launch_manifest.get_plan(launch_plan_name)

    GlobalConfig.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION = False

    GlobalConfig.SHOULD_RESTART_ADB = launch_plan.should_restart_adb
    if GlobalConfig.SHOULD_RESTART_ADB:
        Printer.system_message(TAG, "ADB will be restarted before launching tests.")
    else:
        Printer.system_message(TAG, "ADB with current state will be used during run.")

    GlobalConfig.ADB_SCAN_INTERVAL = launch_plan.adb_scan_interval
    if GlobalConfig.ADB_SCAN_INTERVAL is "":
        Printer.error(TAG, "ADB_SCAN_INTERVAL not specified in LaunchManifest. Launcher will quit.")
        quit()
    else:
        Printer.system_message(TAG, "ADB will be scanned with " + str(GlobalConfig.ADB_SCAN_INTERVAL)
                               + " seconds interval.")

    GlobalConfig.SHOULD_BUILD_NEW_APK = launch_plan.should_build_new_apk
    if GlobalConfig.SHOULD_BUILD_NEW_APK:
        Printer.system_message(TAG, "Launcher will build .*apk candidates for tests with commands specified in test "
                                    "set.")
    else:
        Printer.system_message(TAG, "Launcher will look for existing .*apk candidates for tests. "
                                    "If no usable candidates are found, launcher will build new ones from scratch with "
                                    "commands specified in test set.")

    if ArgLoader.load_avd_set() is not None and ArgLoader.load_avd_set() != ArgLoader.AVD_SET_DEFAULT:
        GlobalConfig.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION = True

        GlobalConfig.SHOULD_RECREATE_EXISTING_AVD = launch_plan.should_recreate_existing_avd
        if GlobalConfig.SHOULD_RECREATE_EXISTING_AVD:

            Printer.system_message(TAG, "If any of AVD which was requested to be used in this run already exists - "
                                        "it will be deleted and created from scratch.")
        else:
            Printer.system_message(TAG, "If any of AVD which was requested to be used in this run already exists - "
                                        "it will be simply launched and used in test session.")

        GlobalConfig.SHOULD_LAUNCH_AVD_SEQUENTIALLY = launch_plan.should_launch_avd_sequentially
        if GlobalConfig.SHOULD_LAUNCH_AVD_SEQUENTIALLY:
            Printer.system_message(TAG,
                                   "AVD will be launched one by one. Wait for start will be performed for each AVD "
                                   "separately and it will take more time.")
        else:
            Printer.system_message(TAG, "AVD will be launched all at once.")
            Printer.error(TAG, "Warning: when launching AVD simultaneously ADB is unaware of the amount of memory that"
                               " specific AVD will use.\nIf there is not enough memory in the system and you launch too"
                               " many AVD at the same time your PC might turn off due to lack of RAM memory.")

        GlobalConfig.AVD_ADB_BOOT_TIMEOUT = launch_plan.avd_adb_boot_timeout_millis
        if GlobalConfig.AVD_ADB_BOOT_TIMEOUT is "":
            Printer.error(TAG, "AVD_ADB_BOOT_TIMEOUT not specified in LaunchManifest. Launcher will quit.")
            quit()
        else:
            Printer.system_message(TAG, "AVD - ADB boot timeout set to " + str(GlobalConfig.AVD_ADB_BOOT_TIMEOUT)
                                   + " seconds.")

        GlobalConfig.AVD_SYSTEM_BOOT_TIMEOUT = launch_plan.avd_system_boot_timeout_millis
        if GlobalConfig.AVD_SYSTEM_BOOT_TIMEOUT is "":
            Printer.error(TAG, "AVD_SYSTEM_BOOT_TIMEOUT not specified in LaunchManifest. Launcher will quit.")
            quit()
        else:
            Printer.system_message(TAG, "AVD - ADB system boot timeout set to "
                                   + str(GlobalConfig.AVD_SYSTEM_BOOT_TIMEOUT) + " seconds.")

    if GlobalConfig.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION:
        Printer.system_message(TAG, "Launcher will use only AVD specified in passed as parameter AVD set.")
    else:
        Printer.system_message(TAG, "Launcher will use all currently visible Android Devices and AVD.")


def init_avd_settings():
    avd_set_name = ArgLoader.load_avd_set()
    avd_set = None
    avd_schema_dict = None
    if avd_set_name is None:
        Printer.system_message(TAG, "No AVD set selected. "
                                    "Currently available real devices will be used in test session.")
    else:
        Printer.message_highlighted(TAG, "Selected avd set: ", avd_set_name)

        avd_manifest_dir = ArgLoader.load_avd_manifest_dir()
        avd_manifest = AvdManifest(avd_manifest_dir)
        Printer.message_highlighted(TAG, "Created AvdManifest from file: ", str(avd_manifest_dir))

        if avd_manifest.contains_set(avd_set_name):
            Printer.system_message(TAG, "AVD set '" + avd_set_name + "' was found in AvdManifest.")
        else:
            Printer.error(TAG, "Invalid AVD set. Set '" + avd_set_name + "' does not exist in AvdManifest!")
            quit()

        avd_set = avd_manifest.get_set(avd_set_name)
        avd_schema_dict = avd_manifest.avd_schema_dict
        for avd in avd_set.avd_list:
            if avd_manifest.contains_schema(avd.avd_name):
                Printer.system_message(TAG, "AVD schema '" + avd.avd_name + "' found in AvdManifest.")
            else:
                Printer.error(TAG, "Set '" + avd_set_name + "' requests usage of AVD schema with name '" +
                              avd.avd_name + "' which doesn't exists in AVD schema list.")
                quit()

    return avd_set, avd_schema_dict


def init_test_settings():
    test_set_name = ArgLoader.load_test_set()
    test_set = None
    test_list = None
    if test_set_name is None:
        Printer.error(TAG, "No test set inserted. Launcher will quit.")
        quit()
    else:
        Printer.message_highlighted(TAG, "Selected test set: ", test_set_name)

        test_manifest_dir = ArgLoader.load_test_manifest_dir()
        test_manifest = TestManifest(test_manifest_dir)
        Printer.message_highlighted(TAG, "Created TestManifest from file: ", str(test_manifest_dir))

        if not test_manifest.test_package_list:
            Printer.error(TAG, "There are no tests specified in TestManifest! Launcher will quit.")
            quit()
        else:
            test_list = test_manifest.test_package_list

        if not test_manifest.contains_set(test_set_name):
            Printer.error(TAG, "Test set '" + test_set_name + "' not found in TestManifest. Launcher will quit.")
            quit()
        else:
            Printer.system_message(TAG, "Test set '" + test_set_name + "' was found in TestManifest.")
            test_set = test_manifest.get_set(test_set_name)
            Printer.message_highlighted(TAG, "Test set contains following package names: ",
                                        ",".join(
                                            "'" + package_name + "'" for package_name in test_set.set_package_names))

            found_all_packages = True
            for package_name in test_set.set_package_names:
                if not test_manifest.contains_package(package_name):
                    found_all_packages = False
                    Printer.error(TAG, "Test package '" + package_name + "' was not found in TestManifest!")

            if found_all_packages:
                Printer.system_message(TAG, "All test packages from set '" + test_set_name
                                       + "' were found in TestManifest.")
            else:
                quit()

            GlobalConfig.INSTRUMENTATION_RUNNER = test_manifest.instrumentation_runner
            if GlobalConfig.INSTRUMENTATION_RUNNER == "":
                Printer.error(TAG, "Instrumentation Runner was not set. "
                                   "Test can't start without it. Launcher will quit.")
            else:
                Printer.message_highlighted(TAG, "Instrumentation Runner set to: ", GlobalConfig.INSTRUMENTATION_RUNNER)

    return test_set, test_list
