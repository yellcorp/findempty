import os.path


__all__ = [
    "ConfigError",
    "any_glob_matcher",
    "load_lines", "loads", "load",
    "get_default_path", "load_default"
]

DEFAULT_PATH = "default_config"

class ConfigError(Exception):
    pass


def any_glob_matcher(*glob_strings):
    def test(path_obj):
        return any(path_obj.match(g) for g in glob_strings)
    return test


TYPE_NOTHING = 0
TYPE_SECTION = 1
TYPE_GLOB = 2

WHITESPACE = "\t\n\r "
COMMENT = "#"
ESCAPE = "\\"

HANDLED_ESCAPES = WHITESPACE + COMMENT
def parse_line(line):
    if line[0] == "[":
        line = line.partition(COMMENT)[0].rstrip()
        if line[-1] != "]":
            raise ConfigError("Bad section header")
        return TYPE_SECTION, line[1:-1]

    buf = [ ]
    in_escape = False
    significant_len = 0
    for ch in line:
        if in_escape:
            if ch not in HANDLED_ESCAPES:
                buf.append(ESCAPE)
            buf.append(ch)
            significant_len = len(buf)
            in_escape = False

        elif ch == ESCAPE:
            in_escape = True

        elif ch == COMMENT:
            break

        else:
            buf.append(ch)
            if ch not in WHITESPACE:
                significant_len = len(buf)

    if in_escape:
        raise ConfigError("Incomplete escape")

    if significant_len == 0:
        return TYPE_NOTHING, None

    return TYPE_GLOB, "".join(buf[:significant_len])


def load_lines(lineiter):
    sections = {
        "ignore": [ ],
        "preserve": [ ]
    }
    target = None

    for line in lineiter:
        line_type, argument = parse_line(line)
        if line_type == TYPE_SECTION:
            target = sections[argument]
        elif line_type == TYPE_GLOB:
            target.append(argument)

    return (
        any_glob_matcher(*sections["ignore"]),
        any_glob_matcher(*sections["preserve"])
    )


def loads(string):
    return load_lines(string.split("\n"))


def load(stream_or_path):
    if isinstance(stream_or_path, (str, bytes)):
        with open(stream_or_path, "r") as stream:
            return load_lines(stream)
    return load_lines(stream_or_path)


def get_default_path():
    return os.path.join(
        os.path.dirname(__file__),
        DEFAULT_PATH
    )


def load_default():
    return load(get_default_path())
