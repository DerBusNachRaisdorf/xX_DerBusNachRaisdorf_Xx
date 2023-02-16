def tokenize_argv(cmd: str) -> list[str]:
    argv: list[str] = []
    cur_token: str = ''
    is_str: bool = False
    is_esc: bool = False
    for c in cmd:
        if c == '"' and not is_esc:
            is_str = not is_str
        elif c == '\\' and not is_esc:
            is_esc = True
        elif is_whitespace(c) and not is_str and not is_esc and cur_token != '':
            argv.append(cur_token)
            cur_token = ''
        else:
            cur_token += c
            is_esc = False
    if cur_token != '':
        argv.append(cur_token)
    return argv


def is_whitespace(char) -> bool:
    return char == ' ' or char == '\t'
