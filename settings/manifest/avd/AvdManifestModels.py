import copy

from settings.loader import JsonLoader


class AvdManifest:
    TAG = "AvdManifest:"

    def __init__(self, manifest_dir):
        self.avd_manifest_source = JsonLoader.load_json(manifest_dir)
        self.avd_schema_dict = dict()
        self.avd_set_dict = dict()

        for avd_schema in self.avd_manifest_source["avd_schema_list"]:
            self.avd_schema_dict.update({avd_schema["avd_name"]: AvdSchema(avd_schema)})

        for avd_set in self.avd_manifest_source["avd_set_list"]:
            self.avd_set_dict.update({avd_set["set_name"]: AvdSet(avd_set)})

    def contains_set(self, set_name):
        set_with_name_found = False
        for key in self.avd_set_dict.keys():
            if key == set_name:
                set_with_name_found = True
                break
        return set_with_name_found

    def get_set(self, set_name):
        avd_set = None
        for key in self.avd_set_dict.keys():
            if key == set_name:
                avd_set = self.avd_set_dict[key]
                break
        return copy.deepcopy(avd_set)

    def contains_schema(self, schema_name):
        schema_with_name_found = False
        for key in self.avd_schema_dict.keys():
            if key == schema_name:
                schema_with_name_found = True
                break
        return schema_with_name_found

    def get_schema(self, schema_name):
        avd_schema = None
        for key in self.avd_schema_dict.keys():
            if key == schema_name:
                avd_schema = self.avd_schema_dict[key]
                break
        return copy.deepcopy(avd_schema)


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


class AvdSet:
    def __init__(self, avd_set_dict):
        self.set_name = avd_set_dict["set_name"]
        self.avd_port_rules = AvdPortRules(avd_set_dict["avd_port_rules"])
        self.avd_list = list()

        for avd in avd_set_dict["avd_list"]:
            self.avd_list.append(AvdInSet(avd))


class AvdPortRules:
    def __init__(self, avd_port_rules_dict):
        self.assign_missing_ports = avd_port_rules_dict["assign_missing_ports"]
        self.search_range_min = avd_port_rules_dict["search_range_min"]
        self.search_range_max = avd_port_rules_dict["search_range_max"]
        self.ports_to_ignore = avd_port_rules_dict["ports_to_ignore"]
        self.ports_to_use = avd_port_rules_dict["ports_to_use"]


class AvdInSet:
    def __init__(self, avd_in_set_dict):
        self.avd_name = avd_in_set_dict["avd_name"]
        self.instances = avd_in_set_dict["instances"]
