class TestSet:
    def __init__(self, test_set_dict):
        self.set_name = test_set_dict["set_name"]
        self.apk_name_part = test_set_dict["apk_name_part"]
        self.application_apk_assemble_task = test_set_dict["application_apk_assemble_task"]
        self.test_apk_assemble_task = test_set_dict["test_apk_assemble_task"]
        self.set_package_names = test_set_dict["set_package_names"]
        self.shard = test_set_dict["shard"]
