def start_wrapper():
    return "<div class=\"wrapper\">"


def add_summary_header(text):
    return "<div class=\"summary_header\">{}</div>".format(text)


def start_summary_table():
    return "<div class=\"summary_table\">"


def start_summary_subtable():
    return "<div class=\"summary_subtable\">"


def start_summary_table_row():
    return "<div class =\"summary_table_row\">"


def add_cell_separator():
    return "<div class=\"summary_table_cell_separator\"></div>"


def add_cell_subseparator():
    return "<div class=\"summary_table_cell_subseparator\"></div>"


def add_summary_table_results_header(text):
    return "<div class=\"summary_table_results_header\">{}</div>".format(text)


def add_summary_table_results_cell(text):
    return "<div class=\"summary_table_results_cell\">{}</div>".format(text)


def add_summary_table_results_passed_left(text):
    return "<div class=\"summary_table_results_passed_cell_left\">{}</div>".format(text)


def add_summary_table_results_passed_right(text):
    return "<div class=\"summary_table_results_passed_cell_right\">{}</div>".format(text)


def add_summary_table_results_failed_left(text):
    return "<div class=\"summary_table_results_failed_cell_left\">{}</div>".format(text)


def add_summary_table_results_failed_right(text):
    return "<div class=\"summary_table_results_failed_cell_right\">{}</div>".format(text)


def add_summary_table_general_header(text):
    return "<div class=\"summary_table_general_header\">{}</div>".format(text)


def add_summary_table_general_cell_left(text):
    return "<div class=\"summary_table_general_cell_left\">{}</div>".format(text)


def add_summary_table_general_cell_right(text):
    return "<div class=\"summary_table_general_cell_right\">{}</div>".format(text)


def add_summary_table_apk_header(text):
    return "<div class=\"summary_table_apk_header\">{}</div>".format(text)


def add_summary_table_apk_subheader(text):
    return "<div class=\"summary_table_apk_subheader\">{}</div>".format(text)


def add_summary_table_apk_cell_left(text):
    return "<div class=\"summary_table_apk_cell_left\">{}</div>".format(text)


def add_summary_table_apk_cell_right(text):
    return "<div class=\"summary_table_apk_cell_right\">{}</div>".format(text)


def add_summary_table_devices_header(text):
    return "<div class=\"summary_table_devices_header\">{}</div>".format(text)


def add_summary_table_devices_subheader(text):
    return "<div class=\"summary_table_devices_subheader\">{}</div>".format(text)


def add_summary_table_devices_cell_left(text):
    return "<div class=\"summary_table_devices_cell_left\">{}</div>".format(text)


def add_summary_table_devices_cell_right(text):
    return "<div class=\"summary_table_devices_cell_right\">{}</div>".format(text)


def end_row():
    return "</div>"


def end_table():
    return "</div>"


def end_wrapper():
    return "</div>"
