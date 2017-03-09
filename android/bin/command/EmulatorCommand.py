class EmulatorCommand:
    class LaunchAvdCommandPart:
        AVD_NAME = "-avd \"{}\""
        AVD_PORT = "-port {}"
        AVD_SNAPSHOT = "-wipe-data -initdata {}"
        AVD_ADDITIONAL_OPTIONS = "{}"
        AVD_OUTPUT = "{}"
