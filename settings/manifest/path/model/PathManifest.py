from settings.loader.JsonLoader import *
from settings.manifest.path.model.PathSet import *
from copy import *

TAG = "PathManifest:"


class PathManifest:
    def __init__(self, manifest_dir):
        self.path_manifest_source = load_json(manifest_dir)
        self.path_set_list = dict()
        for path_set in self.path_manifest_source["path_set_list"]:
            self.path_set_list.update({path_set["set_name"]: PathSet(path_set)})

    def contains_set(self, set_name):
        set_with_name_found = False
        for key in self.path_set_list.keys():
            if key == set_name:
                set_with_name_found = True
                break
        return set_with_name_found

    def get_set(self, set_name):
        path_set = None
        for key in self.path_set_list.keys():
            if key == set_name:
                path_set = self.path_set_list[key]
                break
        return deepcopy(path_set)
