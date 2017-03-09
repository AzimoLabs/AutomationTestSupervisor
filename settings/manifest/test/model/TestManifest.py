from settings.loader.JsonLoader import *
from settings.manifest.test.model.TestPackage import *
from settings.manifest.test.model.TestSet import *
from copy import *

TAG = "TestManifest:"


class TestManifest:
    def __init__(self, manifest_dir):
        self.path_manifest_source = load_json(manifest_dir)
        self.android_app_package = self.path_manifest_source["android_app_package"]
        self.android_test_package = self.path_manifest_source["android_test_package"]
        self.test_package_list = dict()
        self.test_set_list = dict()

        for test_package_dict in self.path_manifest_source["test_package_list"]:
            self.test_package_list.update({test_package_dict["package_name"]: TestPackage(test_package_dict)})

        for test_set_dict in self.path_manifest_source["test_set_list"]:
            self.test_set_list.update({test_set_dict["set_name"]: TestSet(test_set_dict)})

    def contains_package(self, package_name):
        package_with_name_found = False
        for key in self.test_package_list.keys():
            if key == package_name:
                package_with_name_found = True
                break
        return package_with_name_found

    def contains_set(self, set_name):
        set_with_name_found = False
        for key in self.test_set_list.keys():
            if key == set_name:
                set_with_name_found = True
                break
        return set_with_name_found

    def get_package(self, package_name):
        test_package = None
        for key in self.test_package_list.keys():
            if key == package_name:
                test_package = self.test_package_list[key]
                break
        return deepcopy(test_package)

    def get_set(self, set_name):
        test_set = None
        for key in self.test_set_list.keys():
            if key == set_name:
                test_set = self.test_set_list[key]
                break
        return deepcopy(test_set)
