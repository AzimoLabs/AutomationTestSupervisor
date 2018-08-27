def start_test_package_wrapper(toggleable_id):
    return "<div id=\"{}\" class=\"test-package-wrapper\">".format(toggleable_id)


def add_package_header(text):
    return "<div class=\"package-header\">{}</div>".format(text)


def add_test_case_separator():
    return "<div class=\"test-case-separator\"></div>"


def start_passed_test_table():
    return "<div class=\"passed-test-table\">"


def add_passed_test_header(text):
    return "<div class=\"passed-test-header\">{}</div>".format(text)


def start_passed_test_row():
    return "<div class=\"passed-test-row\">"


def add_passed_test_cell(text):
    return "<div class=\"passed-test-cell\">{}</div>".format(text)


def start_failed_table_wrapper():
    return "<div class=\"failed-table-wrapper\">"


def start_failed_test_table():
    return "<div class=\"failed-test-table\">"


def start_failed_test_error_table():
    return "<div class=\"failed-test-error-table\">"


def add_failed_test_header(text):
    return "<div class=\"failed-test-header\">{}</div>".format(text)


def start_failed_test_row():
    return "<div class=\"failed-test-row\">"


def add_failed_test_cell(text):
    return "<div class=\"failed-test-cell\">{}</div>".format(text)


def add_error_cell_light(text):
    return "<div class=\"failed-test-error-light\">{}</div>".format(text)


def add_error_cell_dark(text):
    return "<div class=\"failed-test-error-dark\">{}</div>".format(text)


def start_rerun_table_wrapper():
    return "<div class=\"rerun-table-wrapper\">"


def start_rerun_test_table():
    return "<div class=\"rerun-test-table\">"


def start_rerun_test_error_table():
    return "<div class=\"rerun-test-error-table\">"


def add_rerun_test_header(text):
    return "<div class=\"rerun-test-header\">{}</div>".format(text)


def start_rerun_test_row():
    return "<div class=\"rerun-test-row\">"


def add_rerun_test_cell(text):
    return "<div class=\"rerun-test-cell\">{}</div>".format(text)


def add_rerun_error_cell_light(text):
    return "<div class=\"rerun-test-error-light\">{}</div>".format(text)


def add_rerun_error_cell_dark(text):
    return "<div class=\"rerun-test-error-dark\">{}</div>".format(text)


def end_wrapper():
    return "</div>"


def end_row():
    return "</div>"


def end_table():
    return "</div>"
