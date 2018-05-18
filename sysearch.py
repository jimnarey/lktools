#!/usr/bin/python3

import os


class Node(object):

    def __init__(self, ntype, fspath, dirs, files):
        self.type = ntype
        self.fspath = fspath
        self.dirs = self.resolve_paths(dirs)
        self.files = self.resolve_paths(files)

        for file in self.files:
            setattr(self, file, Node._read_file(self.files[file]))

    def resolve_paths(self, base_names):
        resolved = {}
        for base in base_names:
            resolved[base] = os.path.realpath(os.path.join(self.fspath, base))
        return resolved

    def get(self, name):
        return getattr(self, name, None)

    @staticmethod
    def _read_file(file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.readlines()
        except Exception as e:
            content = str(e)
        return content

    @staticmethod
    def _clean_values(value):
        # Sort out paths
        return value.replace('\n', '')


class Set(object):

    root = '/sys/'

    def __init__(self):
        self.nodes = []
        self._get_nodes()

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
            roots.append([dirpath, dirnames, filenames])
        return roots

    def _get_nodes(self):
        for (dirpath, dirnames, filenames) in Set._get_dirs():
            for filename in filenames:
                if filename == 'path':
                    self.nodes.append(Node('device', dirpath, dirnames, filenames))
            for dirname in dirnames:
                if 'physical_node' in dirname:
                    self.nodes.append(Node(dirname, dirpath, dirnames, filenames))
                elif dirname in ('firmware_node', 'driver'):
                    self.nodes.append(Node(dirname, dirpath, dirnames, filenames))

    # @staticmethod
    # def resolve_path(path):
    #     resolved = {}
    #     for base in base_names:
    #         resolved[base] = os.path.realpath(os.path.join(self.fspath, base))
    #     return resolved

    def count(self):
        return len(self.nodes)

    def search(self, prop, value):
        results = []
        for dev in self.nodes:
            if dev.files[prop]:
                if dev.files[prop] == value:
                    results.append(dev)
        return results


s = Set()

# contents = read_files(file_paths)

print(str(s.count()))

for dev in s.nodes:
    if hasattr(dev, 'path'):
        print(dev.fspath, dev.path)
