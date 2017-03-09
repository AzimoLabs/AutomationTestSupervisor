class AvdPortRules:
    def __init__(self, avd_port_rules_dict):
        self.assign_missing_ports = avd_port_rules_dict["assign_missing_ports"]
        self.search_range_min = avd_port_rules_dict["search_range_min"]
        self.search_range_max = avd_port_rules_dict["search_range_max"]
        self.ports_to_ignore = avd_port_rules_dict["ports_to_ignore"]
        self.ports_to_use = avd_port_rules_dict["ports_to_use"]
