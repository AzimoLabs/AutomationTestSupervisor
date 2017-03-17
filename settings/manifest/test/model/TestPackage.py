class TestPackage:
    def __init__(self, test_package_dict):
        self.test_package_name = test_package_dict["test_package_name"]
        self.test_packages = test_package_dict["test_packages"]
        self.test_classes = test_package_dict["test_classes"]
        self.test_cases = test_package_dict["test_cases"]
