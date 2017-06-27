def add_logcat_header(text):
    return "<div class=\"logcat_header\">{}</div>".format(text)


def start_logcat_table():
    return "<div class=\"logcat_table\">"


def add_debug_row(date, time, tag, level, message):
    row_content = ""
    row_content += "<div class=\"logcat_debug_row\">"
    row_content += "<div class=\"cell centered_cell date_cell\">{}</div>".format(date)
    row_content += "<div class=\"cell centered_cell\">{}</div>".format(time)
    row_content += "<div class=\"cell centered_cell\">{}</div>".format(tag)
    row_content += "<div class=\"cell centered_cell\">{}</div>".format(level)
    row_content += "<div class=\"cell message_cell\">{}</div>".format(message)
    row_content += "</div>"
    return row_content


def add_verbose_row(date, time, tag, level, message):
    row_content = ""
    row_content += "<div class=\"logcat_verbose_row\">"
    row_content += "<div class=\"cell centered_cell date_cell\">{}</div>".format(date)
    row_content += "<div class=\"cell centered_cell\">{}</div>".format(time)
    row_content += "<div class=\"cell centered_cell\">{}</div>".format(tag)
    row_content += "<div class=\"cell centered_cell\">{}</div>".format(level)
    row_content += "<div class=\"cell message_cell\">{}</div>".format(message)
    row_content += "</div>"
    return row_content


def add_info_row(date, time, tag, level, message):
    row_content = ""
    row_content += "<div class=\"logcat_info_row\">"
    row_content += "<div class=\"cell centered_cell date_cell\">{}</div>".format(date)
    row_content += "<div class=\"cell centered_cell\">{}</div>".format(time)
    row_content += "<div class=\"cell centered_cell\">{}</div>".format(tag)
    row_content += "<div class=\"cell centered_cell\">{}</div>".format(level)
    row_content += "<div class=\"cell message_cell\">{}</div>".format(message)
    row_content += "</div>"
    return row_content


def add_warning_row(date, time, tag, level, message):
    row_content = ""
    row_content += "<div class=\"logcat_warning_row\">"
    row_content += "<div class=\"cell centered_cell date_cell\">{}</div>".format(date)
    row_content += "<div class=\"cell centered_cell\">{}</div>".format(time)
    row_content += "<div class=\"cell centered_cell\">{}</div>".format(tag)
    row_content += "<div class=\"cell centered_cell\">{}</div>".format(level)
    row_content += "<div class=\"cell message_cell\">{}</div>".format(message)
    row_content += "</div>"
    return row_content


def add_error_row(date, time, tag, level, message):
    row_content = ""
    row_content += "<div class=\"logcat_error_row\">"
    row_content += "<div class=\"cell centered_cell date_cell\">{}</div>".format(date)
    row_content += "<div class=\"cell centered_cell\">{}</div>".format(time)
    row_content += "<div class=\"cell centered_cell\">{}</div>".format(tag)
    row_content += "<div class=\"cell centered_cell\">{}</div>".format(level)
    row_content += "<div class=\"cell message_cell\">{}</div>".format(message)
    row_content += "</div>"
    return row_content


def end_table():
    return "</div>"
