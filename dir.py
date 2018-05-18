import os


def get_all_roots():
    dirs = set()
    roots = []
    for dirpath, dirnames, filenames in os.walk('/sys/', followlinks=True):
        st = os.stat(dirpath)
        scandirs = []
        for dirname in dirnames:
            st = os.stat(os.path.join(dirpath, dirname))
            dirkey = st.st_dev, st.st_ino
            if dirkey not in dirs:
                dirs.add(dirkey)
                scandirs.append([dirname])
        dirnames[:] = scandirs
        roots.append([dirpath, dirnames, filenames])
    return roots