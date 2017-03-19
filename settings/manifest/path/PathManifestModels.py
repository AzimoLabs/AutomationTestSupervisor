import copy

from settings.loader import JsonLoader


class PathManifest:
    TAG = "PathManifest:"

    def __init__(self, manifest_dir):
        self.path_manifest_source = JsonLoader.load_json(manifest_dir)
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
        return copy.deepcopy(path_set)


class PathSet:
    def __init__(self, path_set_dict):
        self.set_name = path_set_dict["set_name"]
        self.paths = dict()

        for path in path_set_dict["paths"]:
            self.paths.update({path["path_name"]: Path(path)})


class Path:
    def __init__(self, path_dict):
        self.path_name = path_dict["path_name"]
        self.path_value = path_dict["path_value"]
        self.path_description = path_dict["path_description"]
