def start_html():
    return "<html>"


def end_html():
    return "</html>"


def start_head():
    return "<head>"


def end_head():
    return "</head>"


def link_css(css_dir):
    return "<link rel=\"stylesheet\" type=\"text/css\" href=\"{}\">".format(css_dir)


def start_body():
    return "<body>"


def end_body():
    return "</body>"


def create_link_to_file(link_destination, text):
    return "<a href=\"{}\">{}</a>".format(link_destination, text)
