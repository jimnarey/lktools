#!/usr/bin/python3

import os


class Node(object):

    def __init__(self, id, fspath, dirs, files, links, ntype=None, parent=None):
        # print('Node init: ' + ' ' + fspath + ' : ' + str(id))
        self.id = id
        self.type = ntype
        self.fspath = fspath
        self.base_path = os.path.basename(self.fspath)
        self.dirs = self._resolve_paths(dirs)
        self.files = self._resolve_paths(files)
        self.links = self._resolve_paths(links)
        self.file_contents = {}
        self.children = []
        self.parents = []

        if parent:
            self.parents.append(parent)

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

    # def get(self, name):
    #     return getattr(self, name, None)

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
        # self.dir_paths = NodeSet._get_all_dirs(NodeSet.root)
        self.nodes = []

        self._get_dir_nodes(self.root)

    # Get all dirs/subdir paths within a given path

    # Create some root nodes (make the add_node method again) based on a check (e.g. for a path file, multiple)
    # Pass this all the root paths/nodes in turn
    def _get_dir_nodes(self, path, parent=None):
        try:
            for item in os.scandir(path):
                if item.is_dir(follow_symlinks=False):

                    realpath = os.path.realpath(item.path)
                    # print(realpath)
                    if realpath not in [node.fspath for node in self.nodes] and realpath not in self.exclude_dirs:
                        dirnames, filenames, linknames = NodeSet._get_dir_contents(realpath)
                        new_node = Node(NodeSet.get_id(), realpath,
                                               dirnames, filenames, linknames, parent=parent)
                        if parent:
                            parent.children.append(new_node)
                        self.nodes.append(new_node)
                        self._get_dir_nodes(realpath, parent=new_node)
        except PermissionError as e:
            print(str(e))

    def _get_link_nodes(self):
        # realpaths = [node.fspath for node in self.nodes]
        for node in self.nodes:
            for linkname in node.links:
                realpath = os.path.realpath(os.path.join(node.fspath, linkname))
                if os.path.isdir(realpath):
                    existing_node = next((node for node in self.nodes if node.fspath == realpath), None)
                    if existing_node:
                        node.children.append(existing_node)
                        existing_node.parents.append(node)
                    else:
                        dirnames, filenames, linknames = NodeSet._get_dir_contents(realpath)
                        new_node = Node(NodeSet.get_id(), realpath,
                                        dirnames, filenames, linknames, parent=node)
                        node.children.append(new_node)
                        new_node.parents.append(node)
                        self.nodes.append(new_node)

    #
    # @staticmethod
    # def _get_dir_sets(dir_paths):
    #     roots = []
    #     for dir in dir_paths:
    #         # Try to optimise this
    #         ldir = [dir] + list(NodeSet._get_dir_contents(dir))
    #         roots.append(ldir)
    #     return roots

    # Produce a list of dirs, files and links within a single dir
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

    # def _get_nodes(self):
    #     for dirpath, dirnames, filenames, linknames in self.dir_sets:
    #         self.nodes.append(Node(NodeSet.get_id(), 'device', realpath, dirnames, filenames, linknames))

    # Start point for populating nodes
    # def _get_nodes(self):
    #     roots = NodeSet._get_dir_sets(NodeSet.root)
    #     self._get_dev_nodes(roots)
    #     self._get_link_nodes(roots)

    # # Add those dirs which are devices to self.nodes
    # def _get_dev_nodes(self, roots):
    #     for (dirpath, dirnames, filenames, linknames) in roots:
    #         for filename in filenames:
    #             if filename == 'path':
    #                 realpath = os.path.realpath(dirpath)
    #                 self.nodes.append(Node(NodeSet.get_id(), 'device', realpath, dirnames, filenames, linknames))
    #                 break

    # Go through all dirs and call traverse_links on list of links in each dir
    # def _get_link_nodes(self, roots):
    #     for (dirpath, dirnames, filenames, linknames) in roots:
    #         realpath = os.path.realpath(dirpath)
    #         parent_node = self.get_by_fspath(realpath)
    #         self._traverse_links(dirpath, parent_node, linknames)

    # Go through each link list and create/link nodes targeted by each link
    # Needs some work to deal with links (firmware?) which target files, not dirs
    # def _traverse_links(self, dirpath, parent_node, linknames):
    #         for linkname in linknames:
    #             realpath = os.path.realpath(os.path.join(dirpath, linkname))
    #             if realpath not in [node.fspath for node in self.nodes]:
    #                 subdirs, subfiles, sublinks = self._get_dir_contents(realpath)
    #                 if 'physical' in linkname or 'firmware' in linkname:
    #                     self.nodes.append(Node(NodeSet.get_id(), linkname[:8], realpath, subdirs, subfiles, sublinks))
    #                     if parent_node:
    #                         parent_node.children.append(self.nodes[-1])
    #                         self.nodes[-1].parent = parent_node if parent_node else None
    #                     self._traverse_links(self.nodes[-1].fspath, self.nodes[-1], self.nodes[-1].links.keys())
    #                 elif linkname in ('driver',):
    #                     self.nodes.append(Node(NodeSet.get_id(), linkname, realpath, subdirs, subfiles, sublinks))
    #                     if parent_node:
    #                         parent_node.children.append(self.nodes[-1])
    #                         self.nodes[-1].parent = parent_node if parent_node else None
    #                     self._traverse_links(self.nodes[-1].fspath, self.nodes[-1], self.nodes[-1].links.keys())

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



