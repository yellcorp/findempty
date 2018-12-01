import os.path


__all__ = [
    "ParseError", "PresenceMismatch", "TypeMismatch",
    "parse_build", "copy", "compare"
]


def split_indent(text):
    for i in range(len(text)):
        if not text[i].isspace():
            return text[:i], text[i:]
    return text, ""


class ParseError(Exception):
    pass


def parse_build(fs, text_or_lines):
    if isinstance(text_or_lines, str):
        line_iter = text_or_lines.split("\n")
    else:
        line_iter = text_or_lines

    current_indent = None
    current_dir = ""
    header_dir = None

    state = [ ]
    state.append((current_indent, current_dir, header_dir))

    for line_num, line in enumerate(line_iter):
        line = line.rstrip()
        if len(line) == 0:
            continue

        indent, path = split_indent(line)

        if indent != current_indent:
            if current_indent is None:
                current_indent = indent

            elif indent.startswith(current_indent):
                if header_dir is None:
                    raise ParseError("Indent after file", line_num, line)
                state.append((current_indent, current_dir, header_dir))
                current_indent = indent
                current_dir = header_dir
                header_dir = None

            else:
                while indent != current_indent:
                    if len(state) == 0:
                        raise ParseError("Bad dedent", line_num, line)
                    current_indent, current_dir, header_dir = state.pop()

        full_path = current_dir + path
        if path[-1] == "/":
            fs.makedirs(full_path)
            header_dir = full_path
        else:
            fs.touch(full_path)
            header_dir = None


def copy(fs_from, fs_to):
    q = list(fs_from.listdir("."))

    while len(q) > 0:
        path = q.pop()
        if fs_from.is_dir(path):
            fs_to.makedirs(path)
            q.extend(
                os.path.join(path, entry)
                for entry in fs_from.listdir(path)
            )
        else:
            fs_to.touch(path)


def _compare_sets(a, b):
    set_a = set(a)
    set_b = set(b)
    return set_a & set_b, set_a - set_b, set_b - set_a

class PresenceMismatch(object):
    def __init__(self, name, present_in_index):
        self.name = name
        self.present_in_index = present_in_index

    def __str__(self):
        return "Item {!r} is only present in index {}".format(
            self.name, self.present_in_index
        )

    def __repr__(self):
        return "PresenceMismatch({!r}, {!r})".format(
            self.name, self.present_in_index
        )

class TypeMismatch(object):
    def __init__(self, name, types):
        self.name = name
        self.types = tuple(types)

    def __str__(self):
        return "Name {!r} differs in type: {!r}".format(
            self.name, self.types
        )

    def __repr__(self):
        return "TypeMismatch({!r}, {!r})".format(
            self.name, self.types
        )

def compare(fs_a, fs_b):
    q = [ "." ]

    while len(q) > 0:
        dir_path = q.pop()
        a_names = fs_a.listdir(dir_path)
        b_names = fs_b.listdir(dir_path)
        common, only_a, only_b = _compare_sets(a_names, b_names)

        for mismatch_a in only_a:
            yield PresenceMismatch(os.path.join(dir_path, mismatch_a), 0)
        for mismatch_b in only_b:
            yield PresenceMismatch(os.path.join(dir_path, mismatch_b), 1)

        for name in common:
            path = os.path.join(dir_path, name)
            a_isdir = fs_a.is_dir(path)
            b_isdir = fs_b.is_dir(path)
            if a_isdir != b_isdir:
                yield TypeMismatch(
                    path,
                    ("file", "dir")[a_isdir],
                    ("file", "dir")[b_isdir]
                )
            elif a_isdir:
                q.append(path)
