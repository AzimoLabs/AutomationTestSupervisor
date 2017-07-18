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


def start_script():
    return "<script>"


def end_script():
    return "</script>"


def add_toggle_visibility_function_for_package_with_fails():
    return """
    function toggle_visibility_for_package_with_fails(id) {
        var e = document.getElementById(id);

        if (e.style.display === 'none')
            e.style.display = 'block';
        else
            e.style.display = 'none';
    }
    """


def add_toggle_visibility_function_for_clean_package():
    return """
    function toggle_visibility_for_clean_package(id) {
        var e = document.getElementById(id);
    
        if (e.style.display === 'block')
            e.style.display = 'none';
        else
            e.style.display = 'block';
    }
    """


def wrap_in_toggle_visibility_on_click_for_package_with_fails(object_to_be_wrapped, click_id):
    return ("<a class=\"link\" href= \"#\" onclick= \"toggle_visibility_for_package_with_fails('{}'); return false;\""
            + ">{}</a>").format(click_id, object_to_be_wrapped)


def wrap_in_toggle_visibility_on_click_for_clean_package(object_to_be_wrapped, click_id):
    return ("<a class=\"link\" href= \"#\" onclick= \"toggle_visibility_for_clean_package('{}'); return false;\" >{"
            + "}</a>").format(click_id, object_to_be_wrapped)

