class LaunchPlan:
    def __init__(self, launch_plan_dict):
        self.plan_name = launch_plan_dict["plan_name"]
        self.should_restart_adb = launch_plan_dict["should_restart_adb"]
        self.should_recreate_existing_avd = launch_plan_dict["should_recreate_existing_avd"]
        self.should_launch_avd_sequentially = launch_plan_dict["should_launch_avd_sequentially"]
        self.avd_launch_scan_interval_seconds = launch_plan_dict["avd_launch_scan_interval_seconds"]
        self.avd_adb_boot_timeout_seconds = launch_plan_dict["avd_adb_boot_timeout_seconds"]
        self.avd_system_boot_timeout_seconds = launch_plan_dict["avd_system_boot_timeout_seconds"]