# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Project Contributors
#
# Distributed under the terms of the MIT License
# (see spyder/__init__.py for details)
# -----------------------------------------------------------------------------


"""
I/O plugin for loading/saving HDF5 files.

Note that this is a fairly dumb implementation which reads the whole HDF5 file into
Spyder's variable explorer.  Since HDF5 files are designed for storing very large
data-sets, it may be much better to work directly with the HDF5 objects, thus keeping
the data on disk.  Nonetheless, this plugin gives quick and dirty but convenient
access to HDF5 files.

There is no support for creating files with compression, chunking etc, although
these can be read without problem.

All datatypes to be saved must be convertible to a numpy array, otherwise an exception
will be raised.

Data attributes are currently ignored.

When reading an HDF5 file with sub-groups, groups in the HDF5 file will
correspond to dictionaries with the same layout.  However, when saving
data, dictionaries are not turned into HDF5 groups.

TODO: Look for the pytables library if h5py is not found??
TODO: Check issues with valid python names vs valid h5f5 names
"""

import importlib
# Do not import h5py here because it will try to import IPython,
# and this is freezing the Spyder GUI

import numpy as np

if importlib.util.find_spec('h5py'):
    def load_hdf5(filename):
        import h5py
        def get_group(group):
            contents = {}
            for name, obj in list(group.items()):
                if isinstance(obj, h5py.Dataset):
                    contents[name] = np.array(obj)
                elif isinstance(obj, h5py.Group):
                    # it is a group, so call self recursively
                    contents[name] = get_group(obj)
                # other objects such as links are ignored
            return contents

        try:
            f = h5py.File(filename, 'r')
            contents = get_group(f)
            f.close()
            return contents, None
        except Exception as error:
            return None, str(error)

    def save_hdf5(data, filename):
        import h5py
        try:
            f = h5py.File(filename, 'w')
            for key, value in list(data.items()):
                f[key] = np.array(value)
            f.close()
        except Exception as error:
            return str(error)
else:
    load_hdf5 = None
    save_hdf5 = None


if __name__ == "__main__":
    data = {'a' : [1, 2, 3, 4], 'b' : 4.5}
    print(save_hdf5(data, "test.h5"))  # spyder: test-skip
    print(load_hdf5("test.h5"))  # spyder: test-skip
