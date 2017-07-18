def start_wrapper():
    return "<div class=\"summary-wrapper\">"


def add_summary_header(text):
    return "<div class=\"summary-header\">{}</div>".format(text)


def start_summary_table():
    return "<div class=\"summary-table\">"


def start_summary_subtable():
    return "<div class=\"summary-subtable\">"


def start_summary_table_row():
    return "<div class =\"summary-table-row\">"


def add_cell_separator():
    return "<div class=\"summary-table-cell-separator\"></div>"


def add_cell_subseparator():
    return "<div class=\"summary-table-cell-subseparator\"></div>"


def add_summary_table_results_header(text):
    return "<div class=\"summary-table-results-header\">{}</div>".format(text)


def add_summary_table_results_cell(text):
    return "<div class=\"summary-table-results-cell\">{}</div>".format(text)


def add_summary_table_results_passed_left(text):
    return "<div class=\"summary-table-results-passed-cell-left\">{}</div>".format(text)


def add_summary_table_results_passed_right(text):
    return "<div class=\"summary-table-results-passed-cell-right\">{}</div>".format(text)


def add_summary_table_results_failed_left(text):
    return "<div class=\"summary-table-results-failed-cell-left\">{}</div>".format(text)


def add_summary_table_results_failed_right(text):
    return "<div class=\"summary-table-results-failed-cell-right\">{}</div>".format(text)


def add_summary_table_general_header(text):
    return "<div class=\"summary-table-general-header\">{}</div>".format(text)


def add_summary_table_general_cell_left(text):
    return "<div class=\"summary-table-general-cell-left\">{}</div>".format(text)


def add_summary_table_general_cell_right(text):
    return "<div class=\"summary-table-general-cell-right\">{}</div>".format(text)


def add_summary_table_apk_header(text):
    return "<div class=\"summary-table-apk-header\">{}</div>".format(text)


def add_summary_table_apk_subheader(text):
    return "<div class=\"summary-table-apk-subheader\">{}</div>".format(text)


def add_summary_table_apk_cell_left(text):
    return "<div class=\"summary-table-apk-cell-left\">{}</div>".format(text)


def add_summary_table_apk_cell_right(text):
    return "<div class=\"summary-table-apk-cell-right\">{}</div>".format(text)


def add_summary_table_devices_header(text):
    return "<div class=\"summary-table-devices-header\">{}</div>".format(text)


def add_summary_table_devices_subheader(text):
    return "<div class=\"summary-table-devices-subheader\">{}</div>".format(text)


def add_summary_table_devices_cell_left(text):
    return "<div class=\"summary-table-devices-cell-left\">{}</div>".format(text)


def add_summary_table_devices_cell_right(text):
    return "<div class=\"summary-table-devices-cell-right\">{}</div>".format(text)


def start_summary_failed_test_list_table():
    return "<div class =\"summary-failed-test-list-table\">"


def start_summary_failed_test_list_subtable():
    return "<div class =\"summary-failed-test-list-subtable\">"


def start_summary_failed_test_row():
    return "<div class =\"summary-failed-test-row\">"


def add_summary_failed_test_row_cell_light(text):
    return "<div class =\"failed-test-list-light\">{}</div>".format(text)


def add_summary_failed_test_row_cell_dark(text):
    return "<div class =\"failed-test-list-dark\">{}</div>".format(text)


def end_row():
    return "</div>"


def end_table():
    return "</div>"


def end_wrapper():
    return "</div>"
