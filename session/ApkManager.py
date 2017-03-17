from console.Printer import *

TAG = "ApkManager:"


class ApkManager:
    def __init__(self, gradle_controller, apk_provider):
        self.gradle_controller = gradle_controller
        self.apk_provider = apk_provider

    def get_apk_and_build_if_not_found(self, test_set):
        apk_candidate = self.apk_provider.provide_apk(test_set)
        if apk_candidate is None:
            print_error(TAG, "No .apk* candidates for test session were found.")

            print_step(TAG, "Building application and test .*apk from scratch.")
            self.gradle_controller.build_application_apk(test_set)
            self.gradle_controller.build_test_apk(test_set)

            apk_candidate = self.apk_provider.provide_apk(test_set)
            if apk_candidate is None:
                print_error(TAG,
                            "No .apk* candidates for test session were found. Check your config. Launcher will quit.")
                quit()
        return apk_candidate

    def build_apk(self, test_set):
        print_step(TAG, "Building application and test .*apk from scratch.")
        self.gradle_controller.build_application_apk(test_set)
        self.gradle_controller.build_test_apk(test_set)

        apk_candidate = self.apk_provider.provide_apk(test_set)
        if apk_candidate is None:
            print_error(TAG,
                        "No .apk* candidates for test session were found. Check your config. Launcher will quit.")
            quit()
        return apk_candidate
