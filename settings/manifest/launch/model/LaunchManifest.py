from settings.loader.JsonLoader import *
from settings.manifest.launch.model.LaunchPlan import *
from copy import *

TAG = "LaunchManifest:"


class LaunchManifest:
    def __init__(self, manifest_dir):
        self.launch_manifest_source = load_json(manifest_dir)
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
        return deepcopy(launch_plan)
