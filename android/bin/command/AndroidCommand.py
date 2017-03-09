
class AndroidCommand:
    class CreateAvdCommandPart:
        AVD_CREATE = "create avd"
        AVD_NAME = "--name \"{}\""
        AVD_ADDITIONAL_OPTIONS = "{}"
        AVD_TARGET = "--target \"{}\""
        AVD_ABI = "--abi {}"

    LIST_AVD = "list avd"
    DELETE_AVD = "delete avd -n {}"
