def create_table(header, rows):
    table_html = ""

    table_html += _start_table()
    table_html += _create_header_row(header)
    for row_data in rows:
        table_html += _create_row(row_data)
    table_html += _end_table()

    return table_html


def _start_table():
    return """<html><table border="1">"""


def _create_header_row(column_names):
    columns = ""
    for column_name in column_names:
        columns += _column_header(column_name)
    return _row(columns)


def _column_header(column_name):
    return "<th>" + column_name + "</th>"


def _row(row_content_html):
    return "<tr>" + row_content_html + "</tr>"


def _create_row(column_cells):
    columns = ""
    for column_cell_text in column_cells:
        columns += _column_cell(column_cell_text)
    return _row(columns)


def _column_cell(column_cell_text):
    return "<td>" + column_cell_text + "</td>"


def _end_table():
    return "</table></html>"
