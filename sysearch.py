#!/usr/bin/python3

import os


def get_device_roots(start_path):
    device_roots = []
    for (dirpath, dirnames, filenames) in os.walk(start_path):
        for filename in filenames:
            if filename == 'path':
                device_roots.append([dirpath, dirnames, filenames])
    return device_roots


class Device(object):

    def __init__(self, fspath, dirs, files):
        self.fspath = fspath
        self.dirs = self.resolve_paths(dirs)
        self.files = self.resolve_paths(files)

        for file in self.files:
            if file in ('hid', 'path', 'modalias'):
                setattr(self, file, Device._read_file(self.files[file]))

    def resolve_paths(self, base_names):
        resolved = {}
        for base in base_names:
            resolved[base] = os.path.realpath(os.path.join(self.fspath, base))
        return resolved

    @staticmethod
    def _read_file(file_path):
        with open(file_path, 'r') as file:
            return file.readlines()


class Set(object):
    root = '/sys/'

    @classmethod
    def get_device_roots(cls):
        device_roots = []
        for (dirpath, dirnames, filenames) in os.walk(Set.root):
            for filename in filenames:
                if filename == 'path':
                    device_roots.append([dirpath, dirnames, filenames])
        return device_roots

    def __init__(self):
        self.devs = []
        for dev in Set.get_device_roots():
            self.devs.append(Device(dev[0], dev[1], dev[2]))

    def count(self):
        return len(self.devs)

    def search(self, prop, value):
        results = []
        for dev in self.devs:
            if dev.files[prop]:
                if dev.files[prop] == value:
                    results.append(dev)
        return results


s = Set()

# contents = read_files(file_paths)

print(str(s.count()))

for dev in s.devs:
    if dev.path:
        print(dev.fspath, dev.path)
