from __future__ import absolute_import, division, print_function

from collections import deque
from itertools import imap


def foreach(f, iterable):
    deque(imap(f, iterable), maxlen=0)
