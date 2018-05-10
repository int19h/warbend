from __future__ import absolute_import, division, print_function

import os

INDENT = object()
DEDENT = object()


if int(os.getenv('WARBEND_LOG_DATA', 0)):
    log_indent = 0

    def log_data(*args):
        global log_indent
        for arg in args:
            if arg is INDENT:
                log_indent += 1
            elif arg is DEDENT:
                log_indent -= 1
            else:
                s = str(arg).replace('\n', '\n' + '    ' * log_indent)
                print(s, end='')
else:
    log_data = None
