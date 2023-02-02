import re

def is_magic_value(value):
    if value < 100:
        # Do not process non-active repositories
        return False
    value_str = str(value)
    if re.fullmatch("\d0+", str(value)):
        return True
    for i in range(len(value_str) - 1):
        if value_str[i] != value_str[i + 1]:
            return False
    return True


def check_magic_value_range(start, end):
    return [i for i in range(start, end) if is_magic_value(i)]
