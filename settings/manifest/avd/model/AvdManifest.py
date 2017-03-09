from settings.loader.JsonLoader import *
from settings.manifest.avd.model.AvdSchema import *
from settings.manifest.avd.model.AvdSet import *
from copy import *

TAG = "AvdManifest:"


class AvdManifest:
    def __init__(self, manifest_dir):
        self.avd_manifest_source = load_json(manifest_dir)
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
        return deepcopy(avd_set)

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
        return deepcopy(avd_schema)
