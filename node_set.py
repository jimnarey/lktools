import os
from node import Node


class NodeSet(object):

    root = '/sys/'

    def __init__(self):
        self.nodes = []
        self._get_nodes()
        self._link_nodes()

    @staticmethod
    def _get_dirs():
        dirs = set()
        roots = []
        for dirpath, dirnames, filenames in os.walk(NodeSet.root, followlinks=True):
            st = os.stat(dirpath)
            scandirs = []
            for dirname in dirnames:
                st = os.stat(os.path.join(dirpath, dirname))
                dirkey = st.st_dev, st.st_ino
                if dirkey not in dirs:
                    dirs.add(dirkey)
                    scandirs.append(dirname)
            dirnames[:] = scandirs
            roots.append([os.path.realpath(dirpath), dirnames, filenames])
        return roots

    def _get_nodes(self):
        for (dirpath, dirnames, filenames) in NodeSet._get_dirs():
            for filename in filenames:
                if filename == 'path':
                    self.nodes.append(Node('device', dirpath, dirnames, filenames))
            for dirname in dirnames:
                if 'physical_node' in dirname:
                    self.nodes.append(Node(dirname, dirpath, dirnames, filenames))
                elif dirname in ('firmware_node', 'driver'):
                    self.nodes.append(Node(dirname, dirpath, dirnames, filenames))

    def _link_nodes(self):
        for node_a in self.nodes:
            for node_b in self.nodes:
                if node_b.fspath in node_a.dirs.values():
                    node_a.children.append(node_b)
                    node_b.parent = node_a

    def count(self):
        return len(self.nodes)

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
        hids = []
        for dev in devices:
            if dev.get('hid'):
                if dev.hid not in hids:
                    unique_devs.append(dev)
                    hids.append(dev.hid)
            else:
                unique_devs.append(dev)
        return unique_devs

    def has_driver(self):
        has_driver = []
        for dev in self.by_type('device'):
            children = dev.all_children()
            for child in children:
                if child.type == 'driver':
                    has_driver.append(dev)
        return has_driver

    def no_driver(self):
        devices = self.by_type('device')
        has_driver = self.has_driver()
        return [device for device in devices if device not in has_driver]


