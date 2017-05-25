from error.Exceptions import LauncherFlowInterruptedException

from session.SessionDataStores import (
    ApkStore,
    DeviceStore,
    LogStore,
    TestStore
)

from session.SessionManagers import (
    ApkManager,
    DeviceManager,
    TestManager,
    LogManager
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
    AdbSettingsController,
    AdbLogCatController,
    AvdManagerController,
    EmulatorController,
    GradleController,
    InstrumentationRunnerController,
)


class Launcher:
    def __init__(self):
        self.avd_set = None
        self.avd_schemas = None

        self.test_set = None
        self.test_list = None

        self.adb_controller = None
        self.adb_shell_controller = None
        self.adb_package_manager_controller = None
        self.adb_settings_controller = None
        self.adb_logcat_controller = None
        self.avdmanager_controller = None
        self.emulator_controller = None
        self.aapt_controller = None
        self.gradle_controller = None
        self.instrumentation_runner_controller = None

        self.device_store = None
        self.device_manager = None

        self.apk_store = None
        self.apk_manager = None

        self.log_store = None
        self.log_manager = None

        self.test_store = None
        self.test_manager = None

    def _load_config_phase(self):
        Printer.phase("LOADING CONFIG")

        Printer.step("Preparing paths.")
        PathsLoader.init_paths()

        Printer.step("Preparing launch plan.")
        LaunchPlanLoader.init_launch_plan()

        Printer.step("Preparing avd settings.")
        self.avd_set, self.avd_schemas = AvdSetLoader.init_avd_settings()

        Printer.step("Preparing test settings.")
        self.test_set, self.test_list = TestSetLoader.init_test_settings()

    def _object_init_phase(self):
        Printer.phase("OBJECT GRAPH INITIALIZATION")

        Printer.step("Creating objects handling binary file communication.")
        self.adb_controller = AdbController()
        self.adb_shell_controller = AdbShellController()
        self.adb_package_manager_controller = AdbPackageManagerController()
        self.adb_settings_controller = AdbSettingsController()
        self.avdmanager_controller = AvdManagerController()
        self.adb_logcat_controller = AdbLogCatController()
        self.emulator_controller = EmulatorController()
        self.aapt_controller = AaptController()
        self.gradle_controller = GradleController()
        self.instrumentation_runner_controller = InstrumentationRunnerController()

        Printer.step("Creating objects controlling devices.")
        self.device_store = DeviceStore(self.adb_controller,
                                        self.adb_package_manager_controller,
                                        self.adb_settings_controller,
                                        self.avdmanager_controller,
                                        self.emulator_controller)

        self.device_manager = DeviceManager(self.device_store,
                                            self.adb_controller,
                                            self.adb_shell_controller,
                                            self.avdmanager_controller)

        Printer.step("Creating objects handling .*apk file related operations.")
        self.apk_store = ApkStore(self.aapt_controller)
        self.apk_manager = ApkManager(self.device_store,
                                      self.apk_store,
                                      self.gradle_controller,
                                      self.aapt_controller)

        Printer.step("Creating objects handling logging and monitoring.")
        self.log_store = LogStore()
        self.log_manager = LogManager(self.log_store)

        Printer.step("Creating objects controlling test session.")
        self.test_store = TestStore()
        self.test_manager = TestManager(self.instrumentation_runner_controller,
                                        self.adb_shell_controller,
                                        self.adb_logcat_controller,
                                        self.device_store,
                                        self.test_store,
                                        self.log_store)

    def _pre_device_preparation_clean_up_phase(self):
        Printer.phase("PRE-DEVICE PREPARATION CLEAN UP")

        Printer.step("Performing output dir clean up.")
        FileUtils.clean_output_dir()

        Printer.step("Restarting ADB server.")
        if GlobalConfig.SHOULD_RESTART_ADB:
            self.adb_controller.kill_server()
            self.adb_controller.start_server()

    def _device_preparation_phase(self):
        Printer.phase("DEVICE PREPARATION")

        if GlobalConfig.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION:
            Printer.step("Killing currently launched AVD.")

            self.device_manager.add_models_representing_outside_session_virtual_devices()
            if self.device_manager.is_any_avd_visible():
                self.device_manager.kill_all_avd()
            self.device_manager.clear_models_representing_outside_session_virtual_devices()

            if self.avd_set.avd_list:
                Printer.step("Creating models for devices specified in AVD set.")
                self.device_manager.add_models_based_on_avd_schema(self.avd_set, self.avd_schemas)

                if GlobalConfig.SHOULD_RECREATE_EXISTING_AVD:
                    Printer.step("Creating all requested AVD from scratch. Recreating existing ones.")
                    self.device_manager.create_all_avd_and_recreate_existing()
                else:
                    Printer.step("Creating all requested AVD from scratch. Reusing existing ones.")
                    self.device_manager.create_all_avd_and_reuse_existing()
        else:
            Printer.step("Creating models for currently visible Android Devices and AVD.")
            self.device_manager.add_models_representing_outside_session_devices()
            self.device_manager.add_models_representing_outside_session_virtual_devices()

        if GlobalConfig.IGNORED_DEVICE_LIST:
            Printer.step("Checking device ignore list")
            self.device_manager.clear_models_with_android_ids_in_ignore_list()

    def _device_launch_phase(self):
        Printer.phase("DEVICE LAUNCH")

        if GlobalConfig.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION:
            if GlobalConfig.SHOULD_LAUNCH_AVD_SEQUENTIALLY:
                Printer.step("Launching AVD - sequentially.")
                self.device_manager.launch_all_avd_sequentially()
            else:
                Printer.step("Launching AVD - all at once.")
                self.device_manager.launch_all_avd_at_once()
        else:
            Printer.step("Using currently launched devices.")

    def _apk_preparation_phase(self):
        Printer.phase("APK PREPARATION")

        Printer.step("Preparing .*apk for test.")
        if GlobalConfig.SHOULD_BUILD_NEW_APK:
            apk = self.apk_manager.build_apk(self.test_set)
        else:
            apk = self.apk_manager.get_apk(self.test_set)
            if apk is None:
                apk = self.apk_manager.build_apk(self.test_set)

        Printer.step("Scanning .*apk for helpful data.")
        self.apk_manager.set_instrumentation_runner_according_to(apk)

        Printer.step("Installing .*apk on devices included in test session.")
        self.apk_manager.install_apk_on_devices(apk)

    def _pre_test_clean_up_phase(self):
        Printer.phase("PRE-TESTING CLEAN UP")
        pass

    def _testing_phase(self):
        Printer.phase("TESTING")

        Printer.step("Starting tests.")
        self.test_manager.run_with_boosted_shards(self.test_set, self.test_list)

    def _reporting_phase(self):
        Printer.phase("REPORTING")

        Printer.step("Saving logs.")
        self.log_manager.dump_logs_to_file()

    def _finalization_phase(self):
        Printer.phase("FINALIZATION")

        if self.device_manager is not None and self.device_manager.is_any_avd_visible() \
                and GlobalConfig.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION:
            Printer.step("Killing AVD spawned for test session.")
            self.device_manager.kill_all_avd()
            self.device_manager.clear_models_based_on_avd_schema()

    def run(self):
        try:
            self._load_config_phase()
            self._object_init_phase()
            self._pre_device_preparation_clean_up_phase()
            self._device_preparation_phase()
            self._device_launch_phase()
            self._apk_preparation_phase()
            self._pre_test_clean_up_phase()
            self._testing_phase()
            self._reporting_phase()
        except LauncherFlowInterruptedException as e:
            Printer.error(e.caller_tag, str(e))
            quit()
        finally:
            self._finalization_phase()


if __name__ == "__main__":
    launcher = Launcher()
    launcher.run()
