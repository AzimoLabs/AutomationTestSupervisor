def add_logcat_header(text):
    return "<div class=\"logcat-header\">{}</div>".format(text)


def start_logcat_table():
    return "<div class=\"logcat-table\">"


def add_debug_row(date, time, tag, level, message):
    row_content = ""
    row_content += "<div class=\"logcat-debug-row\">"
    row_content += "<div class=\"cell centered-cell date-cell\">{}</div>".format(date)
    row_content += "<div class=\"cell centered-cell\">{}</div>".format(time)
    row_content += "<div class=\"cell centered-cell\">{}</div>".format(tag)
    row_content += "<div class=\"cell centered-cell\">{}</div>".format(level)
    row_content += "<div class=\"cell message-cell\">{}</div>".format(message)
    row_content += "</div>"
    return row_content


def add_verbose_row(date, time, tag, level, message):
    row_content = ""
    row_content += "<div class=\"logcat-verbose-row\">"
    row_content += "<div class=\"cell centered-cell date-cell\">{}</div>".format(date)
    row_content += "<div class=\"cell centered-cell\">{}</div>".format(time)
    row_content += "<div class=\"cell centered-cell\">{}</div>".format(tag)
    row_content += "<div class=\"cell centered-cell\">{}</div>".format(level)
    row_content += "<div class=\"cell message-cell\">{}</div>".format(message)
    row_content += "</div>"
    return row_content


def add_info_row(date, time, tag, level, message):
    row_content = ""
    row_content += "<div class=\"logcat-info-row\">"
    row_content += "<div class=\"cell centered-cell date-cell\">{}</div>".format(date)
    row_content += "<div class=\"cell centered-cell\">{}</div>".format(time)
    row_content += "<div class=\"cell centered-cell\">{}</div>".format(tag)
    row_content += "<div class=\"cell centered-cell\">{}</div>".format(level)
    row_content += "<div class=\"cell message-cell\">{}</div>".format(message)
    row_content += "</div>"
    return row_content


def add_warning_row(date, time, tag, level, message):
    row_content = ""
    row_content += "<div class=\"logcat-warning-row\">"
    row_content += "<div class=\"cell centered-cell date-cell\">{}</div>".format(date)
    row_content += "<div class=\"cell centered-cell\">{}</div>".format(time)
    row_content += "<div class=\"cell centered-cell\">{}</div>".format(tag)
    row_content += "<div class=\"cell centered-cell\">{}</div>".format(level)
    row_content += "<div class=\"cell message-cell\">{}</div>".format(message)
    row_content += "</div>"
    return row_content


def add_error_row(date, time, tag, level, message):
    row_content = ""
    row_content += "<div class=\"logcat-error-row\">"
    row_content += "<div class=\"cell centered-cell date-cell\">{}</div>".format(date)
    row_content += "<div class=\"cell centered-cell\">{}</div>".format(time)
    row_content += "<div class=\"cell centered-cell\">{}</div>".format(tag)
    row_content += "<div class=\"cell centered-cell\">{}</div>".format(level)
    row_content += "<div class=\"cell message-cell\">{}</div>".format(message)
    row_content += "</div>"
    return row_content


def end_table():
    return "</div>"
