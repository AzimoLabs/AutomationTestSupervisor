from settings.manifest.path.model.Path import *


class PathSet:
    def __init__(self, path_set_dict):
        self.set_name = path_set_dict["set_name"]
        self.paths = dict()

        for path in path_set_dict["paths"]:
            self.paths.update({path["path_name"]: Path(path)})
