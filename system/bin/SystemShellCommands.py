class GeneralCommand:
    ANSWER_NO = "echo \"no\" |"
    CHECK_PORT = "lsof -i:{}"
    COPY_FROM_TO = "cat {} > {}"
    DELEGATE_OUTPUT_TO_FILE = "&> {}"
    DELEGATE_OUTPUT_TO_NULL = "&>/dev/null"
    CHANGE_THREAD = "&"
    CHECK_IF_DIR_EXISTS = "ls -d {}"
