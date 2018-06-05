#!/usr/bin/python3

import os


class Node(object):

    def __init__(self, id, fspath, parent=None):
        self.id = id
        self.type = ''
        self.fspath = fspath

        self.base_name = os.path.basename(self.fspath)
        # self._dirs = []
        # self._files = []
        # self._links = []
        self.dirs = {}
        self.files = {}
        self.links = {}
        self.file_contents = {}
        self.children = []
        self.parents = []

        if parent:
            self.parents.append(parent)

        # for file in self.files:
        #     self.file_contents[file] = Node._read_file(self.files[file])

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

    def add_dir(self, name):
        self.dirs[name] = os.path.realpath(os.path.join(self.fspath, name))

    def add_file(self, name):
        self.files[name] = os.path.realpath(os.path.join(self.fspath, name))
        self.file_contents[name] = Node._read_file(self.files[name])

    def add_link(self, name):
        self.links[name] = os.path.realpath(os.path.join(self.fspath, name))

    def all_children(self):
        children = list(self.children)
        for node in self.children:
            children += list(node.children)
        return children


class NodeSet(object):

    next_id = 0

    @classmethod
    def get_id(cls):
        id = cls.next_id
        cls.next_id += 1
        return id

    def __init__(self, root, exclude_dirs):
        self.root = root
        self.exclude_dirs = exclude_dirs
        self.nodes = []
        self._get_dir_nodes(self.root)
        self._get_link_nodes()
        self._classify_nodes()

    def _get_dir_nodes(self, path, parent=None):
        realpath = os.path.realpath(path)
        if realpath not in self.exclude_dirs:

            items = tuple(os.scandir(realpath))
            new_node = Node(NodeSet.get_id(), realpath)

            for item in items:
                try:
                    if item.is_dir(follow_symlinks=False):
                        new_node.add_dir(item.name)
                        self._get_dir_nodes(item.path, parent=new_node)
                except (PermissionError, FileNotFoundError) as e:
                    print(str(e))
                try:
                    if item.is_file(follow_symlinks=False):
                        new_node.add_file(item.name)
                except (PermissionError, FileNotFoundError) as e:
                    print(str(e))
                try:
                    if item.is_symlink():
                        new_node.add_link(item.name)
                except (PermissionError, FileNotFoundError) as e:
                    print(str(e))

            if parent:
                parent.children.append(new_node)
            self.nodes.append(new_node)

    def _get_link_nodes(self):
        for node in self.nodes:
            for linkname in node.links:
                realpath = node.links[linkname]
                if os.path.isdir(realpath):
                    existing_node = next((node for node in self.nodes if node.fspath == realpath), None)
                    if existing_node:
                        node.children.append(existing_node)
                        existing_node.parents.append(node)
                    else:
                        self._get_dir_nodes(realpath, parent=node)

    def _classify_nodes(self):
        for node in self.nodes:
            if 'path' in node.files:
                node.type = 'device'
                continue
            parent_names = (parent.base_name for parent in node.parents)
            if 'physical_node' in parent_names:
                node.type = 'physical_node'
            elif 'driver' in parent_names:
                node.type = 'driver'

    def count(self):
        return len(self.nodes)

    def get_by_id(self, id):
        print(type(id))
        node = [node for node in self.nodes if node.id == int(id)]
        node = node[0] if node else None
        if node:
            print(node.fspath)
        return node

    def get_by_fspath(self, fspath):
        return next((x for x in self.nodes if x.fspath == fspath), None)

    def search_by_file_contents(self, file, value):
        results = []
        for node in self.nodes:
            if node.file_contents.get(file, None):
                if node.file_contents[file] == value:
                    results.append(node)
        return results

    def by_type(self, ntype):
        return [node for node in self.nodes if node.type == ntype]

    def type_contains(self, substring):
        return [node for node in self.nodes if substring in node.type]

    def unique_devs(self):
        devices = self.by_type('device')
        unique_devs = []
        paths = []
        for dev in devices:
            if dev.path not in paths:
                unique_devs.append(dev)
                paths.append(dev.path)
        return unique_devs


exclude_dirs = ('/sys/kernel/security',)

node_set = NodeSet('/sys/', exclude_dirs)

for node in node_set.nodes:
    print(node.id)



