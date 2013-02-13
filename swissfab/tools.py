import functools
import os
from fabric.api import env


class memoized(object):
    """
    Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)


def get_keyfiles(include_dirs=None, include_other_pems=True):
    """
    ssh private keyfiles search function. It's based on similar paramiko code.
    by default it searches .ssh/ssh dir for id_rsa and id_dsa files

    :param include_dirs: list of extra directories to search
    :param include_other_pems: shall function browse for other *.pem files
    :returns: list of keyfiles paths
    """
    key_files = set()
    ssh_dirs = ['~/.ssh', '~/ssh']  # second for windows
    ssh_files = ['id_rsa', 'id_dsa']  # official ssh file names

    if include_dirs:
        ssh_dirs.extend(include_dirs)

    for ssh_dir in ssh_dirs:
        for ssh_file in ssh_files:
            key_filename = os.path.expanduser(os.path.join(ssh_dir, ssh_file))
            if os.path.isfile(key_filename):
                key_files.add(key_filename)
        if include_other_pems:
            for  pem_root, pem_dirs, pem_files in os.walk(ssh_dir):
                for pem_file in pem_files:
                    if pem_file.endswith('.pem'):
                        key_path = os.path.join(pem_root, file)
                        key_files.add(key_path)

    if "key_filename" in env and env.key_filename:
        key_filename = os.path.expanduser(env.key_filename)
        if os.path.isfile(key_filename):
            key_files.add(key_filename)

    return list(key_files)


def project_dir():
    """
    :returns: project directory based on fabfile.py location
    """
    return os.path.dirname(env.real_fabfile)
