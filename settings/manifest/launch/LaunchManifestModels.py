import copy

from settings.loader import JsonLoader


class LaunchManifest:
    TAG = "LaunchManifest:"

    def __init__(self, manifest_dir):
        self.launch_manifest_source = JsonLoader.load_json(manifest_dir)
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
        self.should_restart_adb = launch_plan_dict["should_restart_adb"]
        self.adb_scan_interval_millis = launch_plan_dict["adb_scan_interval_millis"]
        self.should_build_new_apk = launch_plan_dict["should_build_new_apk"]

        self.should_launch_avd_sequentially = launch_plan_dict["should_launch_avd_sequentially"]
        self.should_recreate_existing_avd = launch_plan_dict["should_recreate_existing_avd"]
        self.avd_adb_boot_timeout_millis = launch_plan_dict["avd_adb_boot_timeout_millis"]
        self.avd_system_boot_timeout_millis = launch_plan_dict["avd_system_boot_timeout_millis"]

        self.device_android_id_to_ignore = launch_plan_dict["device_android_id_to_ignore"]
