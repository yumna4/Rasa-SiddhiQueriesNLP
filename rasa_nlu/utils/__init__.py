from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os

import errno
from typing import List
from typing import Optional
from typing import Text


def relative_normpath(f, path):
    # type: (Optional[Text], Text) -> Optional[Text]
    """Return the path of file relative to `path`."""

    if f is not None:
        return os.path.normpath(os.path.relpath(f, path))
    else:
        return None


def create_dir(dir_path):
    # type: (Text) -> None
    """Creates a directory and its super paths. Succeeds even if the path already exists."""

    try:
        os.makedirs(dir_path)
    except OSError as e:
        # be happy if someone already created the path
        if e.errno != errno.EEXIST:
            raise


def create_dir_for_file(file_path):
    # type: (Text) -> None
    """Creates any missing parent directories of this files path."""

    try:
        os.makedirs(os.path.dirname(file_path))
    except OSError as e:
        # be happy if someone already created the path
        if e.errno != errno.EEXIST:
            raise


def lazyproperty(fn):
    """Allows to avoid recomputing a property over and over. Instead the result gets stored in a local var.

    Computation of the property will happen once, on the first call of the property. All succeeding calls will use
    the value stored in the private property."""

    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazyprop(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    return _lazyprop


def list_to_str(l, delim=", ", quote="'"):
    return delim.join([quote + e + quote for e in l])


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def module_path_from_object(o):
    """Returns the fully qualified class path of the instantiated object."""
    return o.__class__.__module__ + "." + o.__class__.__name__


def class_from_module_path(module_path):
    """Given the module name and path of a class, tries to retrieve the class.

    The loaded class can be used to instantiate new objects. """
    import importlib

    # load the module, will raise ImportError if module cannot be loaded
    if "." in module_path:
        module_name, _, class_name = module_path.rpartition('.')
        m = importlib.import_module(module_name)
        # get the class, will raise AttributeError if class cannot be found
        return getattr(m, class_name)
    else:
        return globals()[module_path]
