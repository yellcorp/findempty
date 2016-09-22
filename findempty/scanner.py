import pathlib

__all__ = [ "EmptyFolderScanner" ]


def never(_):
    return False


def nothing():
    pass


class HandlerList(list):
    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)


class EmptyFolderScanner(object):
    def __init__(self, ignore_func=None, preserve_func=None):
        self.ignore_func = ignore_func or never
        self.preserve_func = preserve_func or never

        self.handle_empty_root = HandlerList()
        self.handle_empty_descendant = HandlerList()

        self.log = nothing

    def scan(self, root_path):
        self._scan(pathlib.Path(root_path))

    def _scan(self, path):
        self.log("Scanning {}".format(path))
        keep = False
        for child in path.iterdir():
            is_dir = child.is_dir()

            if is_dir and self.preserve_func(child):
                self.log("Preserving {}".format(child))
                keep = True
            elif self.ignore_func(child):
                self.log("Ignoring {}".format(child))
            elif is_dir:
                child_has_contents = self._scan(child)
                keep = keep or child_has_contents
            else:
                keep = True

        if not keep:
            self.handle_empty_root(path)
            self.log("Walking {}".format(path))
            self._delete_walk(path)

        return keep

    def _delete_walk(self, root):
        for child in root.iterdir():
            is_dir = child.is_dir()
            if is_dir:
                self._delete_walk(child)
            else:
                self.handle_empty_descendant(child, False)
        self.handle_empty_descendant(root, True)
