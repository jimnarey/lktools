#!/usr/bin/python3

import os


class Node(object):

    def __init__(self, id, ntype, fspath, dirs, files):
        self.id = id
        self.type = ntype
        self.fspath = fspath
        # Check symbolic links are added to self.dirs and not to self.files
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


class Set(object):

    root = '/sys/'
    next_id = 0

    @classmethod
    def get_id(cls):
        id = cls.next_id
        cls.next_id += 1
        return id

    def __init__(self):
        self.nodes = []
        self._get_nodes()
        self._link_nodes()

    @staticmethod
    def _get_dirs():
        dirs = set()
        roots = []
        for dirpath, dirnames, filenames in os.walk(Set.root, followlinks=True):
            st = os.stat(dirpath)
            scandirs = []
            for dirname in dirnames:
                st = os.stat(os.path.join(dirpath, dirname))
                dirkey = st.st_dev, st.st_ino
                if dirkey not in dirs:
                    dirs.add(dirkey)
                    scandirs.append(dirname)
            dirnames[:] = scandirs
            # Try doing a realpath here
            roots.append([os.path.realpath(dirpath), dirnames, filenames])
        return roots

    def _get_nodes(self):
        for (dirpath, dirnames, filenames) in Set._get_dirs():
            for filename in filenames:
                if filename == 'path':
                    self.nodes.append(Node(Set.get_id(), 'device', dirpath, dirnames, filenames))
            for dirname in dirnames:
                if 'physical_node' in dirname:
                    self.nodes.append(Node(Set.get_id(), dirname, dirpath, dirnames, filenames))
                elif dirname in ('firmware_node', 'driver'):
                    self.nodes.append(Node(Set.get_id(), dirname, dirpath, dirnames, filenames))

    # def _link_nodes(self):
    #     for node_a in self.nodes:
    #         for node_b in self.nodes:
    #             # Refactor
    #             if node_a.fspath != node_b.fspath and node_b.fspath.startswith(node_a.fspath):
    #                 node_a.children.append(node_b)
    #                 node_b.parent = node_a

    def _link_nodes(self):
        for node_a in self.nodes:
            for node_b in self.nodes:
                if node_b.fspath in node_a.dirs.values():
                    node_a.children.append(node_b)
                    node_b.parent = node_a

    def count(self):
        return len(self.nodes)

    def get_by_id(self, id):
        print(type(id))
        node = [node for node in self.nodes if node.id == int(id)]
        node = node[0] if node else None
        if node:
            print(node.fspath)
        return node


    def search(self, prop, value):
        results = []
        for node in self.nodes:
            if node.files[prop]:
                if node.files[prop] == value:
                    results.append(node)
        return results

    def by_type(self, ntype):
        return [node for node in self.nodes if node.type == ntype]

    def unique_devs(self):
        devices = self.by_type('device')
        unique_devs = []
        paths = []
        for dev in devices:
            if dev.path not in paths:
                unique_devs.append(dev)
                paths.append(dev.path)
        return unique_devs



node_set = Set()

for node in node_set.nodes:
    print(node.id)

# contents = read_files(file_paths)

# print(str(s.count()))


