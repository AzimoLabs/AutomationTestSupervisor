import sys

from android.device.DeviceStore import *
from session.DeviceSessionManager import *
from settings.loader.SettingsLoader import *
from system.manager.FileManager import *

TAG = "Launcher:"

print_step(TAG, "AutomationTestSupervisor has started working!")

print_step(TAG, "Preparing paths.")
init_paths(sys.argv)

print_step(TAG, "Preparing launch plan.")
init_launch_plan(sys.argv)

print_step(TAG, "Preparing avd settings.")
avd_settings_tuple = init_avd_settings(sys.argv)
avd_set = avd_settings_tuple[0]
avd_schemas = avd_settings_tuple[1]

print_step(TAG, "Preparing test settings.")
test_set = init_test_settings(sys.argv)

print_step(TAG, "Initiating objects.")
adb_controller = AdbController()
android_controller = AndroidController()
emulator_controller = EmulatorController()
device_store = DeviceStore(adb_controller, android_controller, emulator_controller)
device_session = DeviceSessionManager(device_store, adb_controller, android_controller)

if output_dir_has_files:
    print_step(TAG, "Performing output dir clean up.")
    clean_output_dir()

if Settings.SHOULD_RESTART_ADB:
    adb_controller.kill_server()
    adb_controller.start_server()

if avd_set.avd_list:
    print_step(TAG, "Preparing AVD instances.")
    device_store.prepare_android_virtual_device_models(avd_set, avd_schemas)

    if Settings.SHOULD_RECREATE_EXISTING_AVD:
        print_step(TAG, "Creating all requested AVD from scratch. Recreating existing ones.")
        device_session.create_all_avd_and_recreate_existing()
    else:
        print_step(TAG, "Creating all requested AVD from scratch. Reusing existing ones.")
        device_session.create_all_avd_and_reuse_existing()

    if Settings.SHOULD_LAUNCH_AVD_SEQUENTIALLY:
        print_step(TAG, "Launching AVD - sequentially.")
        device_session.launch_all_avd_sequentially()
    else:
        print_step(TAG, "Launching AVD - all at once.")
        device_session.launch_all_avd_at_once()

print_step(TAG, "Preparing Android Device instances.")
device_store.prepare_android_device_models()

if avd_set.avd_list:
    print_step(TAG, "Killing all AVD.")
    device_session.kill_all_avd()
