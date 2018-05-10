from __future__ import absolute_import, division, print_function

import sys

try:
    sys.ps1
except AttributeError:
    is_interactive = False
else:
    is_interactive = True

is_quiet = False
