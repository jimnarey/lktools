#!/usr/bin/python3

import os

sys_path = '/sys/'

# sys_path = '/home/jimnarey/'

def safe_recursive_get_dirs(start_path):
	dirs = set()
	for dirpath, dirnames, filenames in os.walk('start_path', followlinks=True):
	    st = os.stat(dirpath)
	    scandirs = []
	    for dirname in dirnames:
	        st = os.stat(os.path.join(dirpath, dirname))
	        dirkey = st.st_dev, st.st_ino
	        if dirkey not in dirs:
	            dirs.add(dirkey)
	            scandirs.append(dirname)
	    dirnames[:] = scandirs
	    print(dirpath)


def get_device_roots(start_path):
	device_roots = []
	for (dirpath, dirnames, filenames) in os.walk(sys_path):
		for filename in filenames:
			if filename == 'path':
				device_roots.append([dirpath, dirnames, filenames])
	return device_roots

# def get_file_paths(start_path):
# 	file_paths = []
# 	# file_sets = []
# 	for (dirpath, dirnames, filenames) in os.walk(sys_path):
# 		print(dirpath, dirnames, filenames)
# 		for filename in filenames:
# 			if filename == 'path':
# 				file_paths.append(os.path.join(dirpath, filename))
# 				# file_sets.append(filenames)
# 	return file_paths, file_sets


# def read_files(file_paths):
# 	contents = []
# 	for file_path in file_paths:
# 		with open(file_path, 'r') as fp:
# 			contents.append(fp.readlines())
# 	return contents

dev_roots = get_device_roots(sys_path)

# contents = read_files(file_paths)

print(str(len(file_paths)))



