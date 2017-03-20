from settings import GlobalConfig
from settings.loader import ArgLoader
from settings.manifest.launch.LaunchManifestModels import LaunchManifest

from system.console import Printer

TAG = "LaunchPlanLoader:"


def init_launch_plan():
    launch_plan_name = _load_launch_plan_name()
    launch_manifest = _load_launch_plan_manifest()
    launch_plan = _load_launch_plan(launch_manifest, launch_plan_name)

    _load_launch_plan_to_global_settings(launch_plan)


def _load_launch_plan_to_global_settings(launch_plan):
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

    avd_set = ArgLoader.get_arg_loaded_by(ArgLoader.AVD_SET_PREFIX)
    if avd_set is not None and avd_set != ArgLoader.AVD_SET_DEFAULT:
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


def _load_launch_plan_name():
    launch_plan_name = ArgLoader.get_arg_loaded_by(ArgLoader.LAUNCH_PLAN_PREFIX)
    if launch_plan_name is None:
        Printer.error(TAG, "No launch plan selected. Launcher will quit.")
        quit()
    else:
        Printer.message_highlighted(TAG, "Selected launch plan: ", launch_plan_name)
    return launch_plan_name


def _load_launch_plan_manifest():
    launch_manifest_dir = ArgLoader.get_arg_loaded_by(ArgLoader.LAUNCH_MANIFEST_DIR_PREFIX)
    launch_manifest = LaunchManifest(launch_manifest_dir)
    Printer.message_highlighted(TAG, "Created LaunchManifest from file: ", str(launch_manifest_dir))
    return launch_manifest


def _load_launch_plan(launch_manifest, launch_plan_name):
    if launch_manifest.contains_plan(launch_plan_name):
        Printer.system_message(TAG, "Launch plan '" + launch_plan_name + "' was found in LaunchManifest.")
        return launch_manifest.get_plan(launch_plan_name)
    else:
        Printer.error(TAG, "Invalid launch plan with name '"
                      + launch_plan_name + "' does not exist in LaunchManifest!")
        quit()
