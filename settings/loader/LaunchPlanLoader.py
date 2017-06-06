from error.Exceptions import LauncherFlowInterruptedException

from settings import GlobalConfig
from settings.loader import ArgLoader
from settings.manifest.launch.LaunchManifestModels import LaunchManifest

from system.console import Printer
from system.console import Color

TAG = "LaunchPlanLoader:"


def init_launch_plan():
    launch_plan_name = _load_launch_plan_name()
    launch_manifest = _load_launch_plan_manifest()
    launch_plan = _load_launch_plan(launch_manifest, launch_plan_name)

    _load_launch_plan_to_global_settings(launch_plan)


def _load_launch_plan_to_global_settings(launch_plan):
    avd_set = ArgLoader.get_arg_loaded_by(ArgLoader.AVD_SET_PREFIX)
    is_avd_session_requested = avd_set is not None and avd_set != ArgLoader.AVD_SET_DEFAULT

    Printer.system_message(TAG, "General:")
    general_settings = launch_plan.general

    if is_avd_session_requested:
        GlobalConfig.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION = True
    else:
        GlobalConfig.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION = False

    GlobalConfig.ADB_CALL_BUFFER_SIZE = general_settings.adb_call_buffer_size
    if GlobalConfig.ADB_CALL_BUFFER_SIZE > 0:
        Printer.system_message(TAG, "  * ADB call buffer size set to: " + Color.GREEN +
                               str(GlobalConfig.ADB_CALL_BUFFER_SIZE) + " slot(s)" + Color.BLUE + ".")
    else:
        message = "ADB_CALL_BUFFER_SIZE cannot be smaller than 1. Launcher will quit."
        raise LauncherFlowInterruptedException(TAG, message)

    GlobalConfig.ADB_CALL_BUFFER_DELAY_BETWEEN_CMD = general_settings.adb_call_buffer_delay_between_cmd
    if GlobalConfig.ADB_CALL_BUFFER_DELAY_BETWEEN_CMD >= 0:
        if GlobalConfig.ADB_CALL_BUFFER_DELAY_BETWEEN_CMD == 0:
            Printer.system_message(TAG, "  * ADB call buffer is disabled. ADB_CALL_BUFFER_DELAY_BETWEEN_CMD"
                                        " param set to: " + + Color.GREEN + "0 second(s)" + + Color.BLUE + ".")
        else:
            Printer.system_message(TAG, "  * ADB call buffer will clear slots after " + Color.GREEN +
                                   str(GlobalConfig.ADB_CALL_BUFFER_DELAY_BETWEEN_CMD / 1000) + " second(s)" +
                                   Color.BLUE + " from ADB call.")
    else:
        message = "ADB_CALL_BUFFER_DELAY_BETWEEN_CMD cannot be negative! Launcher will quit."
        raise LauncherFlowInterruptedException(TAG, message)

    Printer.system_message(TAG, "Device preparation phase settings:")
    device_prep_settings = launch_plan.device_preparation_phase

    if is_avd_session_requested:
        GlobalConfig.SHOULD_RECREATE_EXISTING_AVD = device_prep_settings.avd_should_recreate_existing
        if GlobalConfig.SHOULD_RECREATE_EXISTING_AVD:
            Printer.system_message(TAG, "  * If requested AVD already exists - it will be" + Color.GREEN +
                                   " recreated from scratch" + Color.BLUE + ".")
        else:
            Printer.system_message(TAG, "  * If requested AVD already exists - it will be" + Color.GREEN +
                                   " reused" + Color.BLUE + ".")

    Printer.system_message(TAG, "Device launching phase settings:")
    device_launch_settings = launch_plan.device_launching_phase

    GlobalConfig.IGNORED_DEVICE_LIST = device_launch_settings.device_android_id_to_ignore
    Printer.system_message(TAG, "  * Devices with following Android-IDs will be ignored: " + Color.GREEN +
                           str(GlobalConfig.IGNORED_DEVICE_LIST) + Color.BLUE + ".")

    if is_avd_session_requested:
        GlobalConfig.SHOULD_LAUNCH_AVD_SEQUENTIALLY = device_launch_settings.avd_launch_sequentially
        if GlobalConfig.SHOULD_LAUNCH_AVD_SEQUENTIALLY:
            Printer.system_message(TAG,
                                   "  * AVD will be launched " + Color.GREEN + "one by one" + Color.BLUE +
                                   ". Wait for start will be performed for each AVD separately and it will take more"
                                   " time.")
        else:
            Printer.system_message(TAG, "  * AVD will be launched " + Color.GREEN + "all at once" + Color.BLUE + ".")
            Printer.error(TAG, "Warning: when launching AVD simultaneously ADB is unaware of the amount of memory"
                               " that specific AVD will use. If there is not enough memory in the system and you launch"
                               " too many AVD at the same time your PC might turn off due to lack of RAM memory.")

        GlobalConfig.ADB_SCAN_INTERVAL = device_launch_settings.avd_status_scan_interval_millis
        if GlobalConfig.ADB_SCAN_INTERVAL is "":
            message = "  * ADB_SCAN_INTERVAL not specified in LaunchManifest. Launcher will quit."
            raise LauncherFlowInterruptedException(TAG, message)
        else:
            Printer.system_message(TAG, "  * ADB will be scanned with interval of " + Color.GREEN +
                                   str(GlobalConfig.ADB_SCAN_INTERVAL / 1000) + " second(s)" + Color.BLUE + ".")

        GlobalConfig.AVD_ADB_BOOT_TIMEOUT = device_launch_settings.avd_wait_for_adb_boot_timeout_millis
        if GlobalConfig.AVD_ADB_BOOT_TIMEOUT is "":
            message = "  * AVD_ADB_BOOT_TIMEOUT not specified in LaunchManifest. Launcher will quit."
            raise LauncherFlowInterruptedException(TAG, message)
        else:
            Printer.system_message(TAG, "  * AVD - ADB boot timeout set to " + Color.GREEN +
                                   str(GlobalConfig.AVD_ADB_BOOT_TIMEOUT / 1000) + " second(s)" + Color.BLUE + ".")

        GlobalConfig.AVD_SYSTEM_BOOT_TIMEOUT = device_launch_settings.avd_wait_for_system_boot_timeout_millis
        if GlobalConfig.AVD_SYSTEM_BOOT_TIMEOUT is "":
            message = "  * AVD_SYSTEM_BOOT_TIMEOUT not specified in LaunchManifest. Launcher will quit."
            raise LauncherFlowInterruptedException(TAG, message)
        else:
            Printer.system_message(TAG, "  * AVD - ADB system boot timeout set to " + Color.GREEN +
                                   str(GlobalConfig.AVD_SYSTEM_BOOT_TIMEOUT / 1000) + " second(s)" + Color.BLUE + ".")

    GlobalConfig.SHOULD_RESTART_ADB = device_launch_settings.device_before_launching_restart_adb
    if GlobalConfig.SHOULD_RESTART_ADB:
        Printer.system_message(TAG, "  * " + Color.GREEN + "ADB will be restarted" + Color.BLUE
                               + " before launching tests.")

    Printer.system_message(TAG, "Apk preparation phase settings:")
    apk_preparation_settings = launch_plan.apk_preparation_phase

    GlobalConfig.SHOULD_BUILD_NEW_APK = apk_preparation_settings.build_new_apk
    if GlobalConfig.SHOULD_BUILD_NEW_APK:
        Printer.system_message(TAG, "  * Launcher will " + Color.GREEN + "build .*apk" + Color.BLUE
                               + " for tests with commands specified in test set.")
    else:
        Printer.system_message(TAG, "  * Launcher will " + Color.GREEN + "look for existing .*apk" + Color.BLUE
                               + " look for existing .*apk for tests and try to build only if nothing was found.")

    Printer.system_message(TAG, "Test run  phase settings:")
    testing_phase = launch_plan.testing_phase

    GlobalConfig.SHOULD_RECORD_TESTS = testing_phase.record_tests
    if GlobalConfig.SHOULD_RECORD_TESTS:
        Printer.system_message(TAG, "  * Launcher will " + Color.GREEN + "record device screens" + Color.BLUE
                               + " during test session.")
    else:
        Printer.system_message(TAG, "  * Launcher test " + Color.GREEN + "recording is turned off"
                               + Color.BLUE + ".")


def _load_launch_plan_name():
    launch_plan_name = ArgLoader.get_arg_loaded_by(ArgLoader.LAUNCH_PLAN_PREFIX)

    if launch_plan_name is None:
        message = "No launch plan selected. Launcher will quit."
        raise LauncherFlowInterruptedException(TAG, message)
    else:
        Printer.system_message(TAG, "Selected launch plan: " + Color.GREEN + launch_plan_name + Color.BLUE + ".")
    return launch_plan_name


def _load_launch_plan_manifest():
    launch_manifest_dir = ArgLoader.get_manifest_dir(ArgLoader.LAUNCH_MANIFEST_DIR_KEY)

    if launch_manifest_dir is None:
        message = ("LaunchManifest file directory was not found. Check if config_files_dir_default.json exists in root " 
                   "of project. Otherwise check if it's linking to existing file.")
        raise LauncherFlowInterruptedException(TAG, message)
    else:
        launch_manifest = LaunchManifest(launch_manifest_dir)
        Printer.system_message(TAG, "Created LaunchManifest from file: " + Color.GREEN + launch_manifest_dir
                               + Color.BLUE + ".")
    return launch_manifest


def _load_launch_plan(launch_manifest, launch_plan_name):
    if launch_manifest.contains_plan(launch_plan_name):
        Printer.system_message(TAG, "Launch plan " + Color.GREEN + launch_plan_name + Color.BLUE
                               + " was found in LaunchManifest.")
        return launch_manifest.get_plan(launch_plan_name)
    else:
        message = "Invalid launch plan with name '{}' does not exist in LaunchManifest!"
        message = message.format(launch_plan_name)
        raise LauncherFlowInterruptedException(TAG, message)
