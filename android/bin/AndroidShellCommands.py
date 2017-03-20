class AaptCommand:
    DUMP_BADGING = "dump badging {}"


class AdbCommand:
    KILL_SERVER = "kill-server"
    START_SERVER = "start-server"
    DEVICES = "devices | grep [0-9] | tr -s \"\t\" \" | cut -d\""
    WAIT_FOR_DEVICE = "wait-for-device"
    LIST_AVD = "list avd"
    SPECIFIC_DEVICE = "-s {}"
    INSTALL_APK = "-install {}"
    GET_PROPERTY = "shell getprop"
    KILL_DEVICE = "emu kill"


class AvdManagerCommand:
    class CreateAvdCommandPart:
        AVD_CREATE = "create avd"
        AVD_NAME = "--name \"{}\""
        AVD_PACKAGE = "--package \"{}\""
        AVD_TAG = "--tag \"{}\""
        AVD_ABI = "--abi {}"
        AVD_DEVICE = "--device \"{}\""
        AVD_ADDITIONAL_OPTIONS = "{}"

    LIST_AVD = "list avd"
    DELETE_AVD = "delete avd -n {}"


class EmulatorCommand:
    class LaunchAvdCommandPart:
        AVD_NAME = "-avd \"{}\""
        AVD_PORT = "-port {}"
        AVD_SNAPSHOT = "-wipe-data -initdata {}"
        AVD_ADDITIONAL_OPTIONS = "{}"
        AVD_OUTPUT = "{}"


class GradleCommand:
    RUN_TASK_IN_OTHER_DIRECTORY = "{} -p {} {}"


class InstrumentationRunnerCommand:
    RUN_TEST_PACKAGE = "{} {} shell am instrument -w -e package {} {}"
