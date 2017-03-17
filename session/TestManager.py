from session.thread.TestThread import *
import time

TAG = "TestManager:"


class TestManager:
    def __init__(self, instrumentation_runner_controller, device_store, test_store):
        self.instrumentation_runner_controller = instrumentation_runner_controller
        self.device_store = device_store
        self.test_store = test_store

    def run_tests(self, test_set, test_list):
        self.test_store.get_packages(test_set, test_list)

        for package in self.test_store.packages_to_run:
            test_threads = list()
            for device in self.device_store.get_devices():
                cmd = self.instrumentation_runner_controller.assemble_run_test_package_cmd(device.adb_name, package)
                if device.status == "device":
                    test_thread = TestThread(cmd)
                    test_thread.start()
                    test_threads.append(test_thread)
                else:
                    print_error(TAG, "ALAOSDOASODAKSODASKDA")

            while any(not thread.is_finished for thread in test_threads):
                time.sleep(1)
