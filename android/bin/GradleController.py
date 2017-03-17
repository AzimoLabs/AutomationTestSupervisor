from settings.Settings import *
from android.bin.command.GradleCommand import *
from system.mapper.PathMapper import *
from console.ShellHelper import *
import os

TAG = "GradleController:"


class GradleController:
    gradle_bin = None

    project_root_found = False
    gradlew_found = False

    def __init__(self):
        self.gradle_bin = Settings.PROJECT_ROOT_DIR + "gradlew"

        self.project_root_found = Settings.PROJECT_ROOT_DIR != "" and os.path.isdir(Settings.PROJECT_ROOT_DIR)
        self.gradlew_found = os.path.isfile(self.gradle_bin)

        if self.project_root_found:
            print_message(TAG, "Project root dir '" + Settings.PROJECT_ROOT_DIR
                          + "' was found! Building new .*apk is possible.")
            if self.gradlew_found:
                print_message(TAG, "gradlew binary found at'" + str(self.gradle_bin) + "'.")

    def build_application_apk(self, test_set):
        application_apk_assemble_task = test_set.application_apk_assemble_task
        self._check_if_build_is_possible(application_apk_assemble_task)

        cmd = GradleCommand.RUN_TASK_IN_OTHER_DIRECTORY.format(self.gradle_bin,
                                                               Settings.PROJECT_ROOT_DIR,
                                                               application_apk_assemble_task)
        execute_shell(cmd, True, True)

    def build_test_apk(self, test_set):
        test_apk_assemble_task = test_set.test_apk_assemble_task
        self._check_if_build_is_possible(test_apk_assemble_task)

        cmd = GradleCommand.RUN_TASK_IN_OTHER_DIRECTORY.format(self.gradle_bin,
                                                               Settings.PROJECT_ROOT_DIR,
                                                               test_apk_assemble_task)
        execute_shell(cmd, True, True)

    def _check_if_build_is_possible(self, cmd):
        if cmd == "":
            print_error(TAG, "Gradle assemble task (for building .*apk) was not specified in TestManifest. "
                             "Launcher will quit.")
            quit()
        if not self.project_root_found:
            print_error(TAG, "Unable to build new .*apk. Project root not found. Launcher will quit.")
            quit()
        if not self.gradlew_found:
            print_error(TAG, "Unable to build new .*apk. File 'gradlew' not found in dir '"
                        + Settings.PROJECT_ROOT_DIR + "'. Launcher will quit.")
            quit()
