from __future__ import absolute_import, division, print_function

from io import open
from sys import stderr

from .. import mode


def maybe_open(f, mode, *args, **kwargs):
    if isinstance(f, basestring):
        return open(f, mode, *args, **kwargs)
    if 'r' in mode or '+' in mode:
        f.read
    if 'w' in mode or 'a' in mode or '+' in mode:
        f.write
    return f


def source(f):
    try:
        return f.name
    except AttributeError:
        return repr(f)


def printf(format, *args, **kwargs):
    if not mode.is_quiet:
        return print(format.format(*args, **kwargs), end='')


def eprint(*args, **kwargs):
    if not mode.is_quiet:
        return print(*args, file=stderr, **kwargs)


def eprintf(format, *args, **kwargs):
    return eprint(format.format(*args, **kwargs), end='')
