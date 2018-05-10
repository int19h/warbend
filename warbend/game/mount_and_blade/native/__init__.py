from __future__ import absolute_import, division, print_function

import sys

from ....data import root, parent, transaction
from ...module_system import *
from ... import save
from .. import records
from .slots import Slots

globals().update(records(Slots()))


def load(*args, **kwargs):
    from ... import load
    return load(sys.modules[__name__], *args, **kwargs)
