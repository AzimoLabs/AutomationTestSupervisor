from system.command.GeneralCommand import GeneralCommand


class AdbCommand(GeneralCommand):
    KILL_SERVER = "kill-server"
    START_SERVER = "start-server"
    DEVICES = "devices | grep [0-9] | tr -s \"\t\" \" | cut -d\""
    WAIT_FOR_DEVICE = "wait-for-device"
    LIST_AVD = "list avd"
    SPECIFIC_DEVICE = "-s"
    INSTALL_APK = "-s {} install {}"
    GET_PROPERTY = "shell getprop"
    KILL_DEVICE = "emu kill"
