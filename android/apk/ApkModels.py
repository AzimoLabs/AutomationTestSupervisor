from system.console import Color

MISSING_VALUE = Color.RED + "missing" + Color.END


def _is_field_filled(field):
    return field is not None and field != MISSING_VALUE


def _set_field(field):
    return field if field is not None and field != "" else MISSING_VALUE


class ApkCandidate:
    def __init__(self, apk_name, apk_path, test_apk_name, test_apk_path, apk_version):
        self.apk_name = _set_field(apk_name)
        self.apk_path = _set_field(apk_path)
        self.test_apk_name = _set_field(test_apk_name)
        self.test_apk_path = _set_field(test_apk_path)
        self.apk_version = apk_version

    def is_usable(self):
        return _is_field_filled(self.apk_name) \
               and _is_field_filled(self.test_apk_path) \
               and _is_field_filled(self.test_apk_name) \
               and _is_field_filled(self.test_apk_path) \
               and self.apk_version != -1

    def __str__(self):
        return "Apk('apk_name: " + self.apk_name + "', " \
               + "'apk_path: " + self.apk_path + "', " \
               + "'test_apk_name: " + self.test_apk_name + "', " \
               + "'test_apk_path: " + self.test_apk_path + "', " \
               + "'version_code: " + str(self.apk_version) + "')"
