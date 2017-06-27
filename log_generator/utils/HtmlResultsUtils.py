def add_package_header(text):
    return "<div class=\"package_header\">{}</div>".format(text)


def add_test_case_separator():
    return "<div class=\"test_case_separator\"></div>"


def start_passed_test_table():
    return "<div class=\"passed_test_table\">"


def add_passed_test_header(text):
    return "<div class=\"passed_test_header\">{}</div>".format(text)


def start_passed_test_row():
    return "<div class=\"passed_test_row\">"


def add_passed_test_cell(text):
    return "<div class=\"passed_test_cell\">{}</div>".format(text)


def start_failed_table_wrapper():
    return "<div class=\"failed_table_wrapper\">"


def start_failed_test_table():
    return "<div class=\"failed_test_table\">"


def start_failed_test_error_table():
    return "<div class=\"failed_test_error_table\">"


def add_failed_test_header(text):
    return "<div class=\"failed_test_header\">{}</div>".format(text)


def start_failed_test_row():
    return "<div class=\"failed_test_row\">"


def add_failed_test_cell(text):
    return "<div class=\"failed_test_cell\">{}</div>".format(text)


def add_error_cell_light(text):
    return "<div class=\"failed_test_error_light\">{}</div>".format(text)

def add_error_cell_dark(text):
    return "<div class=\"failed_test_error_dark\">{}</div>".format(text)

def end_wrapper():
    return "</div>"


def end_row():
    return "</div>"


def end_table():
    return "</div>"
