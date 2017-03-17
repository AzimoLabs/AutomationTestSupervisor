from android.apk.ApkProvider import *
from android.bin.AaptController import *
from android.bin.GradleController import *
from android.bin.InstrumentationRunnerController import *
from android.device.DeviceStore import *
from android.test.TestStore import *
from session.ApkManager import *
from session.DeviceManager import *
from session.TestManager import *
from settings.loader.SettingsLoader import *
from system.manager.FileManager import *

TAG = "Launcher:"

print_step(TAG, "AutomationTestSupervisor has started working!")

print_step(TAG, "Preparing paths.")
init_paths()

print_step(TAG, "Preparing launch plan.")
init_launch_plan()

print_step(TAG, "Preparing avd settings.")
avd_set, avd_schemas = init_avd_settings()

print_step(TAG, "Preparing test settings.")
test_set, test_list = init_test_settings()

print_step(TAG, "Initiating objects.")
adb_controller = AdbController()
android_controller = AvdManagerController()
emulator_controller = EmulatorController()
aapt_controller = AaptController()
gradle_controller = GradleController()
instrumentation_runner_controller = InstrumentationRunnerController()

device_store = DeviceStore(adb_controller, android_controller, emulator_controller)
device_manager = DeviceManager(device_store, adb_controller, android_controller)

apk_provider = ApkProvider(aapt_controller)
apk_manager = ApkManager(gradle_controller, apk_provider)

test_store = TestStore()
test_manager = TestManager(instrumentation_runner_controller, device_store, test_store)

if output_dir_has_files:
    print_step(TAG, "Performing output dir clean up.")
    clean_output_dir()

try:
    if Settings.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION:
        if avd_set.avd_list:
            if device_manager.is_any_avd_visible():
                print_step(TAG, "Killing currently visible AVD.")
                device_manager.kill_all_avd()

            print_step(TAG, "Preparing AVD instances according to AVD set.")
            device_manager.add_models_based_on_avd_schema(avd_set, avd_schemas)

            if Settings.SHOULD_RECREATE_EXISTING_AVD:
                print_step(TAG, "Creating all requested AVD from scratch. Recreating existing ones.")
                device_manager.create_all_avd_and_recreate_existing()
            else:
                print_step(TAG, "Creating all requested AVD from scratch. Reusing existing ones.")
                device_manager.create_all_avd_and_reuse_existing()

            if Settings.SHOULD_LAUNCH_AVD_SEQUENTIALLY:
                print_step(TAG, "Launching AVD - sequentially.")
                device_manager.launch_all_avd_sequentially()
            else:
                print_step(TAG, "Launching AVD - all at once.")
                device_manager.launch_all_avd_at_once()
    else:
        print_step(TAG, "Preparing Android Device instances.")
        device_manager.add_models_representing_outside_session_devices()

    print_step(TAG, "Restarting ADB server.")
    if Settings.SHOULD_RESTART_ADB:
        adb_controller.kill_server()
        adb_controller.start_server()

    print_step(TAG, "Preparing .*apk for test.")
    if Settings.SHOULD_BUILD_NEW_APK:
        apk = apk_manager.build_apk(test_set)
    else:
        apk = apk_manager.get_apk_and_build_if_not_found(test_set)
    print_message_highlighted(TAG, "Picked .*apk with highest version code:\n", str(apk))

    print_step(TAG, "Installing .*apk on devices included in test session.")
    device_manager.install_apk_on_devices(apk)

    print_step(TAG, "Starting tests.")
    test_manager.run_tests(test_set, test_list)

finally:
    if device_manager.is_any_avd_visible() and Settings.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION:
        print_step(TAG, "Killing AVD spawned for test session.")
        device_manager.kill_all_avd()
