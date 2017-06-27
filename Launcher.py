from error.Exceptions import LauncherFlowInterruptedException

from session.SessionDataStores import (
    DeviceStore,
    ApkStore,
    TestStore
)
from session import SessionGlobalLogger as session_logger
from session.SessionManagers import (
    CleanUpManager,
    DeviceManager,
    ApkManager,
    TestManager,
)

from settings import (
    GlobalConfig,
    Version
)
from settings.loader import (
    PathsLoader,
    LaunchPlanLoader,
    AvdSetLoader,
    TestSetLoader
)

from system.console import Printer
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

from log_generator import LogGenerator


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

        self.log_store = None
        self.log_manager = None

        self.device_store = None
        self.device_manager = None

        self.apk_store = None
        self.apk_manager = None

        self.test_store = None
        self.test_manager = None

        self.clean_up_manager = None

    @staticmethod
    def _init_phase():
        Printer.phase("INIT")
        session_logger.log_session_start_time()

        Printer.step("Launcher started working!")
        Version.info()
        Version.python_check()

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

        Printer.step("Creating objects controlling test session.")
        self.test_store = TestStore()
        self.test_manager = TestManager(self.instrumentation_runner_controller,
                                        self.adb_controller,
                                        self.adb_shell_controller,
                                        self.adb_logcat_controller,
                                        self.device_store,
                                        self.test_store)

        Printer.step("Creating objects handling clean up.")
        self.clean_up_manager = CleanUpManager(self.device_store,
                                               self.adb_controller,
                                               self.adb_shell_controller)

    def _pre_device_preparation_clean_up_phase(self):
        Printer.phase("PRE-DEVICE PREPARATION CLEAN UP")

        Printer.step("Clean-up of launcher output directories")
        self.clean_up_manager.prepare_output_directories()

        Printer.step("Restarting ADB server.")
        if GlobalConfig.SHOULD_RESTART_ADB:
            self.clean_up_manager.restart_adb()

    def _device_preparation_phase(self):
        Printer.phase("DEVICE PREPARATION")

        if GlobalConfig.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION:
            Printer.step("Killing currently launched AVD.")
            session_logger.log_total_device_creation_start_time()

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

            session_logger.log_total_device_creation_end_time()
        else:
            Printer.step("Creating models for currently visible Android Devices and AVD.")
            self.device_manager.add_models_representing_outside_session_devices()
            self.device_manager.add_models_representing_outside_session_virtual_devices()

        if not self.device_manager.is_any_avd_visible():
            quit()

        if GlobalConfig.IGNORED_DEVICE_LIST:
            Printer.step("Checking device ignore list")
            self.device_manager.clear_models_with_android_ids_in_ignore_list()

    def _device_launch_phase(self):
        Printer.phase("DEVICE LAUNCH")
        session_logger.log_total_device_launch_start_time()

        if GlobalConfig.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION:
            if GlobalConfig.SHOULD_LAUNCH_AVD_SEQUENTIALLY:
                Printer.step("Launching AVD - sequentially.")
                self.device_manager.launch_all_avd_sequentially()
            else:
                Printer.step("Launching AVD - all at once.")
                self.device_manager.launch_all_avd_at_once()
        else:
            Printer.step("Using currently launched devices.")

        session_logger.log_total_device_launch_end_time()

    def _apk_preparation_phase(self):
        Printer.phase("APK PREPARATION")
        session_logger.log_total_apk_build_start_time()

        Printer.step("Preparing .*apk for test.")
        if GlobalConfig.SHOULD_BUILD_NEW_APK:
            apk = self.apk_manager.build_apk(self.test_set)
        else:
            apk = self.apk_manager.get_existing_apk(self.test_set)
            if apk is None:
                apk = self.apk_manager.build_apk(self.test_set)
        self.apk_manager.display_picked_apk_info()

        Printer.step("Scanning .*apk for helpful data.")
        self.apk_manager.set_instrumentation_runner_according_to(apk)

        session_logger.log_total_apk_build_end_time()

    def _apk_installation_phase(self):
        Printer.phase("APK INSTALLATION")
        session_logger.log_total_apk_install_start_time()

        Printer.step("Installing .*apk on devices included in test session.")
        apk = self.apk_manager.get_existing_apk(self.test_set)
        self.apk_manager.install_apk_on_devices(apk)

        session_logger.log_total_apk_install_end_time()

    def _pre_test_clean_up_phase(self):
        Printer.phase("PRE-TESTING CLEAN UP")

        if GlobalConfig.SHOULD_RECORD_TESTS:
            Printer.step("Preparing directory for recordings storage on test devices")
            self.clean_up_manager.prepare_device_directories()

    def _testing_phase(self):
        Printer.phase("TESTING")
        session_logger.log_total_test_start_time()

        Printer.step("Starting tests.")
        self.test_manager.run_tests(self.test_set, self.test_list)

        session_logger.log_total_test_end_time()

    def _finalization_phase(self):
        Printer.phase("FINALIZATION")

        Printer.step("Displaying saved files during test session.")
        session_logger.dump_saved_files_history()

        Printer.step("Session summary.")
        session_logger.log_session_end_time()
        session_logger.save_session_summary()
        session_logger.dump_session_summary()
        LogGenerator.generate_logs(self.test_set)

        if self.device_manager is not None and self.device_manager.is_any_avd_visible() \
                and GlobalConfig.SHOULD_USE_ONLY_DEVICES_SPAWNED_IN_SESSION:
            Printer.step("Killing AVD spawned for test session.")
            self.device_manager.kill_all_avd()
            self.device_manager.clear_models_based_on_avd_schema()

    def run(self):
        try:
            self._init_phase()
            self._load_config_phase()
            self._object_init_phase()
            self._pre_device_preparation_clean_up_phase()
            self._device_preparation_phase()
            self._device_launch_phase()
            self._apk_preparation_phase()
            self._apk_installation_phase()
            self._pre_test_clean_up_phase()
            self._testing_phase()
        except LauncherFlowInterruptedException as e:
            Printer.error(e.caller_tag, str(e))
            quit()
        finally:
            self._finalization_phase()


if __name__ == "__main__":
    launcher = Launcher()
    launcher.run()
