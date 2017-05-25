import copy

from system.file import FileUtils


class LaunchManifest:
    TAG = "LaunchManifest:"

    def __init__(self, manifest_dir):
        self.launch_manifest_source = FileUtils.load_json(manifest_dir)
        self.launch_plan_dict = dict()

        for launch_plan in self.launch_manifest_source["launch_plan_list"]:
            self.launch_plan_dict.update({launch_plan["plan_name"]: LaunchPlan(launch_plan)})

    def contains_plan(self, plan_name):
        plan_with_name_found = False
        for key in self.launch_plan_dict.keys():
            if key == plan_name:
                plan_with_name_found = True
                break
        return plan_with_name_found

    def get_plan(self, plan_name):
        launch_plan = None
        for key in self.launch_plan_dict.keys():
            if key == plan_name:
                launch_plan = self.launch_plan_dict[key]
                break
        return copy.deepcopy(launch_plan)


class LaunchPlan:
    def __init__(self, launch_plan_dict):
        self.plan_name = launch_plan_dict["plan_name"]
        self.general = LaunchGeneralOptions(launch_plan_dict["general"])
        self.device_preparation_phase = DevicePreparationPhaseOptions(launch_plan_dict["device_preparation_phase"])
        self.device_launching_phase = DeviceLaunchingPhaseOptions(launch_plan_dict["device_launching_phase"])
        self.apk_preparation_phase = ApkPreparationPhaseOptions(launch_plan_dict["apk_preparation_phase"])
        self.testing_phase = TestingPhaseOptions(launch_plan_dict["testing_phase"])


class LaunchGeneralOptions:
    def __init__(self, general_options_dict):
        self.adb_call_buffer_size = general_options_dict["adb_call_buffer_size"]
        self.adb_call_buffer_delay_between_cmd = general_options_dict["adb_call_buffer_delay_between_cmd"]


class DevicePreparationPhaseOptions:
    def __init__(self, device_preparation_phase_dict):
        self.avd_should_recreate_existing = device_preparation_phase_dict["avd_should_recreate_existing"]


class DeviceLaunchingPhaseOptions:
    def __init__(self, launching_phase_dict):
        self.device_android_id_to_ignore = launching_phase_dict["device_android_id_to_ignore"]
        self.avd_launch_sequentially = launching_phase_dict["avd_launch_sequentially"]
        self.avd_status_scan_interval_millis = launching_phase_dict["avd_status_scan_interval_millis"]
        self.avd_wait_for_adb_boot_timeout_millis = launching_phase_dict["avd_wait_for_adb_boot_timeout_millis"]
        self.avd_wait_for_system_boot_timeout_millis = launching_phase_dict["avd_wait_for_system_boot_timeout_millis"]
        self.device_before_launching_restart_adb = launching_phase_dict["device_before_launching_restart_adb"]


class ApkPreparationPhaseOptions:
    def __init__(self, apk_preparation_phase_dict):
        self.build_new_apk = apk_preparation_phase_dict["build_new_apk"]


class TestingPhaseOptions:
    def __init__(self, testing_phase_dict):
        self.record_tests = testing_phase_dict["record_tests"]
