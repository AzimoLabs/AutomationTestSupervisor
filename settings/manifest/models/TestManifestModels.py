import copy

from system.file import FileUtils


class TestManifest:
    TAG = "TestManifest:"

    def __init__(self, manifest_dir):
        self.path_manifest_source = FileUtils.load_json(manifest_dir)
        self.test_package_list = dict()
        self.test_set_list = dict()

        for test_package_dict in self.path_manifest_source["test_list"]:
            self.test_package_list.update({test_package_dict["test_package_name"]: TestPackage(test_package_dict)})

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
        return copy.deepcopy(test_package)

    def get_set(self, set_name):
        test_set = None
        for key in self.test_set_list.keys():
            if key == set_name:
                test_set = self.test_set_list[key]
                break
        return copy.deepcopy(test_set)


class TestPackage:
    def __init__(self, test_package_dict):
        self.test_package_name = test_package_dict["test_package_name"]
        self.test_packages = test_package_dict["test_packages"]
        self.test_classes = test_package_dict["test_classes"]
        self.test_cases = test_package_dict["test_cases"]


class TestSet:
    def __init__(self, test_set_dict):
        self.set_name = test_set_dict["set_name"]
        self.apk_name_part = test_set_dict["apk_name_part"]
        self.application_apk_assemble_task = test_set_dict["application_apk_assemble_task"]
        self.test_apk_assemble_task = test_set_dict["test_apk_assemble_task"]
        self.set_package_names = test_set_dict["set_package_names"]
        self.gradle_build_params = test_set_dict["gradle_build_params"]
        self.shard = test_set_dict["shard"]
