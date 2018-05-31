import os


class Node(object):

    def __init__(self, ntype, fspath, dirs, files):
        self.type = ntype
        self.fspath = fspath
        self.dirs = self._resolve_paths(dirs)
        self.files = self._resolve_paths(files)
        self.children = []
        self.parent = 'no_parent'

        for file in self.files:
            setattr(self, file, Node._read_file(self.files[file]))

    @staticmethod
    def _read_file(file_path):
        try:
            with open(file_path, 'r') as file:
                content = Node._clean_values(file.read())
        except Exception as e:
            content = str(e)
        return content

    @staticmethod
    def _clean_values(value):
        # Sort out paths
        return value.replace('\n', '')

    def _resolve_paths(self, base_names):
        resolved = {}
        for base in base_names:
            resolved[base] = os.path.realpath(os.path.join(self.fspath, base))
        return resolved

    def get(self, name):
        return getattr(self, name, None)

    def all_children(self):
        children = list(self.children)
        for node in self.children:
            children += list(node.children)
        return children
