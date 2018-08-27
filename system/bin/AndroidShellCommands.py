class AaptCommand:
    DUMP_BADGING = "dump badging {}"
    LIST_ALL = "l -a {}"


class AdbCommand:
    KILL_SERVER = "kill-server"
    START_SERVER = "start-server"
    DEVICES = "devices"
    WAIT_FOR_DEVICE = "wait-for-device"
    LIST_AVD = "list avd"
    KILL_DEVICE = "emu kill"
    SPECIFIC_DEVICE = "-s {}"
    INSTALL_APK = "install {}"
    UNINSTALL_PACKAGE = "uninstall {}"
    PULL = "pull {} {}"


class AdbShellCommand:
    SHELL = "shell"
    CREATE_DIR = "mkdir {}"
    REMOVE_FILE = "rm -f {}"
    REMOVE_FILES_IN_DIR = "rm -r {}"
    RECORD = "screenrecord --bit-rate 2000000 {}"
    GET_PROPERTY = "getprop {}"


class AdbPackageManagerCommand:
    PACKAGE_MANAGER = "pm"
    CLEAR_CACHE = "clear {}"
    LIST_SERVICES = "list packages"
    UNINSTALL_PACKAGE = "uninstall {}"


class AdbActivityManagerCommand:
    ACTIVITY_MANAGER = "am"


class AdbSettingsCommand:
    SETTINGS = "settings"
    GET_DEVICE_ANDROID_ID = "get secure android_id"


class AdbLogCatCommand:
    LOG_CAT = "logcat"
    FLUSH = "-b all -c"
    DUMP = "-d"


class InstrumentationRunnerCommand:
    INSTRUMENT_PROCESS = "instrument -w"
    NUM_SHARD = "-e numShards {}"
    SHARD_INDEX = "-e shardIndex {}"
    PACKAGE = "-e package {}"
    DISPLAY_RAW_MESSAGE = "-r"
    INSTRUMENTATION_RUNNER = "{}"
    CLASS = "-e class {}"
    TEST_CASE = "#{}"

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
