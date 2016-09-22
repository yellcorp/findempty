import os.path


__all__ = [ "Live", "Mock" ]


class Live(object):
    def __init__(self, root):
        self.root = root

    def _resolve(self, path):
        return os.path.join(self.root, path)

    def makedirs(self, path):
        os.makedirs(self._resolve(path), exist_ok=True)

    def touch(self, path):
        with open(self._resolve(path), "w") as stream:
            print("touched", file=stream)

    def listdir(self, path):
        for name in os.listdir(self._resolve(path)):
            yield name

    def exists(self, path):
        return os.path.exists(self._resolve(path))

    def is_dir(self, path):
        return os.path.isdir(self._resolve(path))

    def is_file(self, path):
        return os.path.isfile(self._resolve(path))


class Mock(object):
    class Error(Exception):
        pass

    class File(object):
        def __init__(self, name):
            self.name = name

        def is_file(self):
            return True

        def is_dir(self):
            return False

    class Directory(object):
        def __init__(self, name):
            self.name = name
            self.entries = { }

        def is_file(self):
            return False

        def is_dir(self):
            return True

    def __init__(self):
        self._root = Mock.Directory("")

    def _get(self, path):
        node = self._root
        for part in self._iter_parts(path):
            if part not in node.entries:
                return None
            node = node.entries[part]
        return node

    def _get_dir(self, path):
        node = self._get(path)
        if node is None or not node.is_dir():
            raise Mock.Error("Not a directory: " + path)
        return node

    def makedirs(self, path):
        node = self._root
        history = [ ]
        for part in self._iter_parts(path):
            history.append(part)
            if part not in node.entries:
                node.entries[part] = Mock.Directory(part)
            node = node.entries[part]
            if not node.is_dir():
                raise Mock.Error("Not a directory: " + "/".join(history))

    def touch(self, path):
        container, name = os.path.split(path)
        dir_node = self._get_dir(container)
        node = dir_node.entries.get(name)
        if node is None:
            dir_node.entries[name] = Mock.File(name)
        elif not node.is_file():
            raise Mock.Error("Not a file: " + path)

    def listdir(self, path):
        dir_node = self._get_dir(path)
        for k in dir_node.entries.keys():
            yield k

    def exists(self, path):
        return self._get(path) is not None

    def is_dir(self, path):
        node = self._get(path)
        return node is not None and node.is_dir()

    def is_file(self, path):
        node = self._get(path)
        return node is not None and node.is_file()

    @staticmethod
    def _iter_parts(path):
        for part in path.split("/"):
            if part and part != ".":
                yield part
