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
