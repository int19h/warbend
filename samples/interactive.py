from __future__ import absolute_import, division, print_function

import locale
locale.setlocale(locale.LC_ALL, '')
del locale

import warbend.mode
warbend.mode.is_interactive = True

import warbend
from warbend.game.module_system import *  # pylint: disable=W0614
from warbend.game.mount_and_blade import *  # pylint: disable=W0614


try:
    __import__('ptpython.repl').repl.embed(globals(), locals())
except ImportError:
    __import__('code').interact(local=globals())
