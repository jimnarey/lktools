#!/usr/bin/python3

import os


class Node(object):

    def __init__(self, id, ntype, fspath, dirs, files, links):
        self.id = id
        self.type = ntype
        self.fspath = fspath
        self.base_path = os.path.basename(self.fspath)
        self.dirs = self._resolve_paths(dirs)
        self.files = self._resolve_paths(files)
        self.links = self._resolve_paths(links)
        self.file_contents = {}
        self.children = []
        self.parent = None

        for file in self.files:
            self.file_contents[file] = Node._read_file(self.files[file])

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

    @staticmethod
    def _get_roots(path):
        roots = []
        for dir in Set._get_dirs(path):
            ldir = [dir] + list(Set._get_dir_contents(dir))
            roots.append(ldir)
        return roots

    @staticmethod
    def _get_dirs(path):
        dirs = []
        try:
            for item in os.scandir(path):
                if item.is_dir(follow_symlinks=False):
                    dirs.append(item.path)
                    dirs += Set._get_dirs(item.path)
        except PermissionError as e:
            print(str(e))
        return dirs

    @staticmethod
    def _get_dir_contents(path):
        dirs = []
        files = []
        links = []
        try:
            for item in os.scandir(path):
                if item.is_dir(follow_symlinks=False):
                    dirs.append(item.name)
                if item.is_file(follow_symlinks=False):
                    files.append(item.name)
                if item.is_symlink():
                    links.append(item.name)
        except (PermissionError, FileNotFoundError) as e:
            print(str(e))
        return dirs, files, links

    def _get_nodes(self):
        roots = Set._get_roots(Set.root)
        self._get_dev_nodes(roots)
        self._get_link_nodes(roots)

    def _get_dev_nodes(self, roots):
        for (dirpath, dirnames, filenames, linknames) in roots:
            for filename in filenames:
                if filename == 'path':
                    realpath = os.path.realpath(dirpath)
                    self.nodes.append(Node(Set.get_id(), 'device', realpath, dirnames, filenames, linknames))
                    break

    def _get_link_nodes(self, roots):
        for (dirpath, dirnames, filenames, linknames) in roots:
            realpath = os.path.realpath(dirpath)
            parent_node = self.get_by_fspath(realpath)
            self._traverse_links(dirpath, parent_node, linknames)

    def _traverse_links(self, dirpath, parent_node, linknames):
            for linkname in linknames:
                realpath = os.path.realpath(os.path.join(dirpath, linkname))
                if realpath not in [node.fspath for node in self.nodes]:
                    subdirs, subfiles, sublinks = self._get_dir_contents(realpath)
                    if 'physical' in linkname or 'firmware' in linkname:
                        self.nodes.append(Node(Set.get_id(), linkname[:8], realpath, subdirs, subfiles, sublinks))
                        if parent_node:
                            parent_node.children.append(self.nodes[-1])
                            self.nodes[-1].parent = parent_node if parent_node else None
                        self._traverse_links(self.nodes[-1].fspath, self.nodes[-1], self.nodes[-1].links.keys())
                    elif linkname in ('driver',):
                        self.nodes.append(Node(Set.get_id(), linkname, realpath, subdirs, subfiles, sublinks))
                        if parent_node:
                            parent_node.children.append(self.nodes[-1])
                            self.nodes[-1].parent = parent_node if parent_node else None
                        self._traverse_links(self.nodes[-1].fspath, self.nodes[-1], self.nodes[-1].links.keys())

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


node_set = Set()

for node in node_set.nodes:
    print(node.id)



