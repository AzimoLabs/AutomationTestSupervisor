from settings.manifest.avd.model.AvdPortRules import *
from settings.manifest.avd.model.AvdInSet import *


class AvdSet:
    def __init__(self, avd_set_dict):
        self.set_name = avd_set_dict["set_name"]
        self.avd_port_rules = AvdPortRules(avd_set_dict["avd_port_rules"])
        self.avd_list = list()

        for avd in avd_set_dict["avd_list"]:
            self.avd_list.append(AvdInSet(avd))
