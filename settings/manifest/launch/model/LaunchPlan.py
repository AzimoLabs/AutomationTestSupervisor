class LaunchPlan:
    def __init__(self, launch_plan_dict):
        self.plan_name = launch_plan_dict["plan_name"]
        self.should_restart_adb = launch_plan_dict["should_restart_adb"]
        self.adb_scan_interval = launch_plan_dict["adb_scan_interval"]
        self.should_build_new_apk = launch_plan_dict["should_build_new_apk"]

        self.should_launch_avd_sequentially = launch_plan_dict["should_launch_avd_sequentially"]
        self.should_recreate_existing_avd = launch_plan_dict["should_recreate_existing_avd"]
        self.avd_adb_boot_timeout_millis = launch_plan_dict["avd_adb_boot_timeout_millis"]
        self.avd_system_boot_timeout_millis = launch_plan_dict["avd_system_boot_timeout_millis"]
