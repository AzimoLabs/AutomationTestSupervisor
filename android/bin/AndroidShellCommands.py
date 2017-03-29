class AaptCommand:
    DUMP_BADGING = "dump badging {}"


class AdbCommand:
    KILL_SERVER = "kill-server"
    START_SERVER = "start-server"
    DEVICES = "devices | grep [0-9] | tr -s \"\t\" \" | cut -d\""
    WAIT_FOR_DEVICE = "wait-for-device"
    LIST_AVD = "list avd"
    KILL_DEVICE = "emu kill"
    SPECIFIC_DEVICE = "-s {}"
    INSTALL_APK = "install {}"
    UNINSTALL_PACKAGE = "uninstall {}"


class AdbShellCommand:
    SHELL = "shell"
    GET_PROPERTY = "getprop {}"


class AdbPackageManagerCommand:
    PACKAGE_MANAGER = "pm"
    LIST_SERVICES = "list packages"
    UNINSTALL_PACKAGE = "uninstall {}"


class AdbActivityManagerCommand:
    ACTIVITY_MANAGER = "am"


class InstrumentationRunnerCommand:
    INSTRUMENT_PROCESS = "instrument -w"
    NUM_SHARD = "-e numShards {}"
    SHARD_INDEX = "-e shardIndex {}"
    PACKAGE = "-e package {}"
    INSTRUMENTATION_RUNNER = "{}"
    RUN_TEST_PACKAGE = "{} {} shell am instrument -w -e package {} {}"


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
