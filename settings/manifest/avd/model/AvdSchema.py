class AvdSchema:
    def __init__(self, avd_schema_dict):
        self.avd_name = avd_schema_dict["avd_name"]
        self.create_avd_package = avd_schema_dict["create_avd_package"]
        self.create_avd_device = avd_schema_dict["create_device"]
        self.create_avd_tag = avd_schema_dict["create_avd_tag"]
        self.create_avd_abi = avd_schema_dict["create_avd_abi"]
        self.create_avd_hardware_config_filepath = avd_schema_dict["create_avd_hardware_config_filepath"]
        self.create_avd_additional_options = avd_schema_dict["create_avd_additional_options"]
        self.launch_avd_snapshot_filepath = avd_schema_dict["launch_avd_snapshot_filepath"]
        self.launch_avd_launch_binary_name = avd_schema_dict["launch_avd_launch_binary_name"]
        self.launch_avd_additional_options = avd_schema_dict["launch_avd_additional_options"]
