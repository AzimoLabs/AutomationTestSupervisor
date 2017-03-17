from settings.Settings import *
from settings.loader.ArgLoader import *
from settings.manifest.avd.model.AvdManifest import *
from settings.manifest.launch.model.LaunchManifest import *
from settings.manifest.path.model.PathManifest import *
from settings.manifest.test.model.TestManifest import *
from system.mapper.PathMapper import *
from console.Printer import *

TAG = "SettingsLoader:"

ANDROID_HOME_ENV = os.getenv('ANDROID_HOME')
ANDROID_SDK_HOME_ENV = os.getenv('ANDROID_SDK_HOME')

OUTPUT_DIR_DEFAULT = "output"


def init_paths():
    path_set_name = load_path_set()
    if path_set_name is None:
        print_error(TAG, "No path set was selected. Launcher will quit.")
        quit()
    else:
        print_message_highlighted(TAG, "Selected path set: ", path_set_name)

    path_manifest_dir = load_path_manifest_dir()
    path_manifest = PathManifest(path_manifest_dir)
    print_message_highlighted(TAG, "Created PathManifest from file: ", str(path_manifest_dir))

    if path_manifest.contains_set(path_set_name):
        print_message(TAG, "Path set '" + path_set_name + "' was found in PathManifest.")
    else:
        print_error(TAG, "Invalid path set with name '"
                    + path_set_name + "' does not exist in PathManifest!")
        quit()

    path_set = path_manifest.get_set(path_set_name)

    Settings.SDK_DIR = add_ending_slash(clean_path((path_set.paths["sdk_dir"]).path_value))
    if Settings.SDK_DIR == "":
        print_message(TAG, "SDK path not set in PathManifest. Will use path set in env variable 'ANDROID_HOME'.")
        if ANDROID_HOME_ENV is None:
            print_error(TAG, "Env variable 'ANDROID_HOME' is not set. Launcher will quit.")
            quit()
        else:
            Settings.SDK_DIR = add_ending_slash(clean_path(ANDROID_HOME_ENV))
    print_message_highlighted(TAG, "Launcher will look for SDK at dir: ", Settings.SDK_DIR)

    Settings.AVD_DIR = add_ending_slash(clean_path((path_set.paths["avd_dir"]).path_value))
    if Settings.AVD_DIR == "":
        print_message(TAG, "AVD path not set in PathManifest. Will use path set in env variable 'ANDROID_SDK_HOME'.")
        if ANDROID_SDK_HOME_ENV is None:
            print_message(TAG,
                          "Env variable 'ANDROID_SDK_HOME' is not set. Trying to recreate default path from user root.")
            Settings.AVD_DIR = add_ending_slash(clean_path("~")) + ".android"
    print_message_highlighted(TAG, "Launcher will look for AVD images at dir: ", Settings.AVD_DIR)

    Settings.OUTPUT_DIR = add_ending_slash(clean_path((path_set.paths["output_dir"]).path_value))
    if Settings.OUTPUT_DIR == "":
        print_message(TAG, "Output path not set in PathManifest. Default value will be used.")
        Settings.OUTPUT_DIR = OUTPUT_DIR_DEFAULT
    print_message_highlighted(TAG, "Launcher will generate log from tests in dir: ", Settings.OUTPUT_DIR)

    Settings.PROJECT_ROOT_DIR = add_ending_slash(clean_path((path_set.paths["project_root_dir"]).path_value))
    if Settings.PROJECT_ROOT_DIR == "":
        print_message(TAG, "Project root was not specified. This field is not obligatory.")
        print_error(TAG, "Warning: Without project root directory launcher will quit if no "
                         ".*apk files will be found in directory lodaded from 'apk_dir' field of PathManifest.")
    else:
        print_message_highlighted(TAG, "Project root dir: ", Settings.PROJECT_ROOT_DIR)

    Settings.APK_DIR = add_ending_slash(clean_path((path_set.paths["apk_dir"]).path_value))
    if Settings.APK_DIR == "":
        print_error(TAG, "Directory with .*apk files was not found. Launcher will quit.")
        quit()
    print_message_highlighted(TAG, "Launcher will look for .*apk files in dir: ", Settings.APK_DIR)


def init_launch_plan():
    launch_plan_name = load_launch_plan()
    if launch_plan_name is None:
        print_error(TAG, "No launch plan selected. Launcher will quit.")
        quit()
    else:
        print_message_highlighted(TAG, "Selected launch plan: ", launch_plan_name)

    launch_manifest_dir = load_launch_manifest_dir()
    launch_manifest = LaunchManifest(launch_manifest_dir)
    print_message_highlighted(TAG, "Created LaunchManifest from file: ", str(launch_manifest_dir))

    if launch_manifest.contains_plan(launch_plan_name):
        print_message(TAG, "Launch plan '" + launch_plan_name + "' was found in LaunchManifest.")
    else:
        print_error(TAG, "Invalid launch plan with name '"
                    + launch_plan_name + "' does not exist in LaunchManifest!")
        quit()

    launch_plan = launch_manifest.get_plan(launch_plan_name)

    Settings.SHOULD_RESTART_ADB = launch_plan.should_restart_adb
    if Settings.SHOULD_RESTART_ADB:
        print_message(TAG, "Adb will be restarted before launching tests.")
    else:
        print_message(TAG, "Adb with current state will be used during run.")

    Settings.SHOULD_BUILD_NEW_APK = launch_plan.should_build_new_apk
    if Settings.SHOULD_BUILD_NEW_APK:
        print_message(TAG, "Launcher will build .*apk candidates for tests with commands specified in test set.")
    else:
        print_message(TAG, "Launcher will look for existing .*apk candidates for tests. If no usable candidates are "
                           "found, launcher will build new ones from scratch with commands specified in test set.")

    Settings.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION = launch_plan.should_use_only_devices_spawned_in_session
    if Settings.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION:
        print_message(TAG, "Launcher will use only AVD specified in passed as parameter AVD set.")
    else:
        print_message(TAG, "Launcher will use all currently visible Android Devices and AVD.")

    if load_avd_set() is not None:
        Settings.SHOULD_RECREATE_EXISTING_AVD = launch_plan.should_recreate_existing_avd
        if Settings.SHOULD_RECREATE_EXISTING_AVD:
            print_message(TAG, "If any of AVD which was requested to be used in this run already exists - "
                               "it will be deleted and created from scratch.")
        else:
            print_message(TAG, "If any of AVD which was requested to be used in this run already exists - "
                               "it will be simply launched and used in test session.")

        Settings.SHOULD_LAUNCH_AVD_SEQUENTIALLY = launch_plan.should_launch_avd_sequentially
        if Settings.SHOULD_LAUNCH_AVD_SEQUENTIALLY:
            print_message(TAG,
                          "AVD will be launched one by one. Wait for start will be performed for each AVD separately"
                          " and it will take more time.")
        else:
            print_message(TAG, "AVD will be launched all at once.")
            print_error(TAG, "Warning: when launching AVD simultaneously ADB is unaware of the amount of memory that"
                             " specific AVD will use.\nIf there is not enough memory in the system and you launch too"
                             " many AVD at the same time your PC might turn off due to lack of RAM memory.")

        Settings.AVD_LAUNCH_SCAN_INTERVAL = launch_plan.avd_launch_scan_interval_millis
        if Settings.AVD_LAUNCH_SCAN_INTERVAL is "":
            print_error(TAG, "AVD_LAUNCH_SCAN_INTERVAL not specified in LaunchManifest. Launcher will quit.")
            quit()
        else:
            print_message(TAG, "AVD status during launch will be scanned with " + str(Settings.AVD_LAUNCH_SCAN_INTERVAL)
                          + " seconds interval.")

        Settings.AVD_ADB_BOOT_TIMEOUT = launch_plan.avd_adb_boot_timeout_millis
        if Settings.AVD_ADB_BOOT_TIMEOUT is "":
            print_error(TAG, "AVD_ADB_BOOT_TIMEOUT not specified in LaunchManifest. Launcher will quit.")
            quit()
        else:
            print_message(TAG, "AVD - adb boot timeout set to " + str(Settings.AVD_ADB_BOOT_TIMEOUT) + " seconds.")

        Settings.AVD_SYSTEM_BOOT_TIMEOUT = launch_plan.avd_system_boot_timeout_millis
        if Settings.AVD_SYSTEM_BOOT_TIMEOUT is "":
            print_error(TAG, "AVD_SYSTEM_BOOT_TIMEOUT not specified in LaunchManifest. Launcher will quit.")
            quit()
        else:
            print_message(TAG, "AVD - adb system boot timeout set to "
                          + str(Settings.AVD_SYSTEM_BOOT_TIMEOUT) + " seconds.")


def init_avd_settings():
    avd_set_name = load_avd_set()
    avd_set = None
    avd_schema_dict = None
    if avd_set_name is None:
        print_message(TAG, "No AVD set selected. Currently available real devices will be used in test session.")
    else:
        print_message_highlighted(TAG, "Selected avd set: ", avd_set_name)

        avd_manifest_dir = load_avd_manifest_dir()
        avd_manifest = AvdManifest(avd_manifest_dir)
        print_message_highlighted(TAG, "Created AvdManifest from file: ", str(avd_manifest_dir))

        if avd_manifest.contains_set(avd_set_name):
            print_message(TAG, "AVD set '" + avd_set_name + "' was found in AvdManifest.")
        else:
            print_error(TAG, "Invalid AVD set. Set '" + avd_set_name + "' does not exist in AvdManifest!")
            quit()

        avd_set = avd_manifest.get_set(avd_set_name)
        avd_schema_dict = avd_manifest.avd_schema_dict
        for avd in avd_set.avd_list:
            if avd_manifest.contains_schema(avd.avd_name):
                print_message(TAG, "AVD schema '" + avd.avd_name + "' found in AvdManifest.")
            else:
                print_error(TAG, "Set '" + avd_set_name + "' requests usage of AVD schema with name '" +
                            avd.avd_name + "' which doesn't exists in AVD schema list.")
                quit()

    return avd_set, avd_schema_dict


def init_test_settings():
    test_set_name = load_test_set()
    test_set = None
    test_list = None
    if test_set_name is None:
        print_error(TAG, "No test set inserted. Launcher will quit.")
        quit()
    else:
        print_message_highlighted(TAG, "Selected test set: ", test_set_name)

        test_manifest_dir = load_test_manifest_dir()
        test_manifest = TestManifest(test_manifest_dir)
        print_message_highlighted(TAG, "Created TestManifest from file: ", str(test_manifest_dir))

        if not test_manifest.test_package_list:
            print_error(TAG, "There are no tests specified in TestManifest! Launcher will quit.")
            quit()
        else:
            test_list = test_manifest.test_package_list

        if not test_manifest.contains_set(test_set_name):
            print_error(TAG, "Test set '" + test_set_name + "' not found in TestManifest. Launcher will quit.")
            quit()
        else:
            print_message(TAG, "Test set '" + test_set_name + "' was found in TestManifest.")
            test_set = test_manifest.get_set(test_set_name)
            print_message_highlighted(TAG, "Test set contains following package names: ",
                                      ",".join("'" + package_name + "'" for package_name in test_set.set_package_names))

            found_all_packages = True
            for package_name in test_set.set_package_names:
                if not test_manifest.contains_package(package_name):
                    found_all_packages = False
                    print_error(TAG, "Test package '" + package_name + "' was not found in TestManifest!")

            if found_all_packages:
                print_message(TAG, "All test packages from set '" + test_set_name + "' were found in TestManifest.")
            else:
                quit()

            Settings.INSTRUMENTATION_RUNNER = test_manifest.instrumentation_runner
            if Settings.INSTRUMENTATION_RUNNER == "":
                print_error(TAG, "Instrumentation Runner was not set. Test can't start without it. Launcher will quit.")
            else:
                print_console_highlighted(TAG, "Instrumentation Runner set to: ", Settings.INSTRUMENTATION_RUNNER)

    return test_set, test_list
