from error.Exceptions import LauncherFlowInterruptedException

from session.SessionDataStores import (
    ApkStore,
    DeviceStore,
    TestStore
)

from session.SessionManagers import (
    ApkManager,
    DeviceManager,
    TestManager
)

from settings import GlobalConfig
from settings.loader import (
    PathsLoader,
    LaunchPlanLoader,
    AvdSetLoader,
    TestSetLoader
)

from system.console import Printer
from system.file import FileUtils
from system.bin.AndroidBinaryFileControllers import (
    AaptController,
    AdbController,
    AdbShellController,
    AdbPackageManagerController,
    AvdManagerController,
    EmulatorController,
    GradleController,
    InstrumentationRunnerController,
)

TAG = "Launcher:"

adb_controller = None
adb_shell_controller = None
adb_package_manager_controller = None
avdmanager_controller = None
emulator_controller = None
aapt_controller = None
gradle_controller = None
instrumentation_runner_controller = None

device_store = None
device_manager = None

apk_store = None
apk_manager = None

test_store = None
test_manager = None

if __name__ == "__main__":
    try:
        Printer.step(TAG, "AutomationTestSupervisor has started working!")

        Printer.step(TAG, "Preparing paths.")
        PathsLoader.init_paths()

        Printer.step(TAG, "Preparing launch plan.")
        LaunchPlanLoader.init_launch_plan()

        Printer.step(TAG, "Preparing avd settings.")
        avd_set, avd_schemas = AvdSetLoader.init_avd_settings()

        Printer.step(TAG, "Preparing test settings.")
        test_set, test_list = TestSetLoader.init_test_settings()

        Printer.step(TAG, "Initiating objects.")
        adb_controller = AdbController()
        adb_shell_controller = AdbShellController()
        adb_package_manager_controller = AdbPackageManagerController()
        avdmanager_controller = AvdManagerController()
        emulator_controller = EmulatorController()
        aapt_controller = AaptController()
        gradle_controller = GradleController()
        instrumentation_runner_controller = InstrumentationRunnerController()

        device_store = DeviceStore(adb_controller, adb_package_manager_controller, avdmanager_controller,
                                   emulator_controller)
        device_manager = DeviceManager(device_store, adb_controller, adb_shell_controller, avdmanager_controller)

        apk_store = ApkStore(aapt_controller)
        apk_manager = ApkManager(device_store, apk_store, gradle_controller, aapt_controller)

        test_store = TestStore()
        test_manager = TestManager(instrumentation_runner_controller, device_store, test_store)

        if FileUtils.output_dir_has_files:
            Printer.step(TAG, "Performing output dir clean up.")
            FileUtils.clean_output_dir()

        if GlobalConfig.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION:
            Printer.step(TAG, "Preparing device session - killing currently launched AVD.")
            device_manager.add_models_representing_outside_session_virtual_devices()
            if device_manager.is_any_avd_visible():
                device_manager.kill_all_avd()
            device_manager.clear_models_representing_outside_session_virtual_devices()

            if avd_set.avd_list:
                Printer.step(TAG, "Preparing device session - creating models for devices specified in AVD set.")
                device_manager.add_models_based_on_avd_schema(avd_set, avd_schemas)

                if GlobalConfig.SHOULD_RECREATE_EXISTING_AVD:
                    Printer.step(TAG, "Creating all requested AVD from scratch. Recreating existing ones.")
                    device_manager.create_all_avd_and_recreate_existing()
                else:
                    Printer.step(TAG, "Creating all requested AVD from scratch. Reusing existing ones.")
                    device_manager.create_all_avd_and_reuse_existing()

                if GlobalConfig.SHOULD_LAUNCH_AVD_SEQUENTIALLY:
                    Printer.step(TAG, "Launching AVD - sequentially.")
                    device_manager.launch_all_avd_sequentially()
                else:
                    Printer.step(TAG, "Launching AVD - all at once.")
                    device_manager.launch_all_avd_at_once()
        else:
            Printer.step(TAG, "Preparing device session - creating models for currently visible Android Devices "
                              "and AVD.")
            device_manager.add_models_representing_outside_session_devices()
            device_manager.add_models_representing_outside_session_virtual_devices()

        Printer.step(TAG, "Restarting ADB server.")
        if GlobalConfig.SHOULD_RESTART_ADB:
            adb_controller.kill_server()
            adb_controller.start_server()

        Printer.step(TAG, "Preparing .*apk for test.")
        if GlobalConfig.SHOULD_BUILD_NEW_APK:
            apk = apk_manager.build_apk(test_set)
        else:
            apk = apk_manager.get_apk(test_set)
            if apk is None:
                apk = apk_manager.build_apk(test_set)

        Printer.step(TAG, "Scanning .*apk for helpful data.")
        apk_manager.set_instrumentation_runner_according_to(apk)

        Printer.step(TAG, "Installing .*apk on devices included in test session.")
        apk_manager.install_apk_on_devices(apk)

        Printer.step(TAG, "Starting tests.")
        test_manager.run_with_boosted_shards(test_set, test_list)

    except LauncherFlowInterruptedException as e:
        Printer.error(e.caller_tag, str(e))
        quit()

    finally:
        if device_manager is not None and device_manager.is_any_avd_visible() \
                and GlobalConfig.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION:
            Printer.step(TAG, "Killing AVD spawned for test session.")
            device_manager.kill_all_avd()
            device_manager.clear_models_based_on_avd_schema()

        Printer.step(TAG, "Launcher finished work!")
