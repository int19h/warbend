from __future__ import absolute_import, division, print_function

from .. import mode
from .transaction import Transaction


class Context(object):
    __slots__ = ['source', 'mutable', 'observed', 'transaction']

    def __init__(self, root=None):
        self.source = None
        self.mutable = {}
        self.observed = []
        self.transaction = Transaction(self)

    def observe(self, obj):
        if self.observed:
            self.observed.append(obj)

    def begin_observation(self):
        self.observed[:] = [None]

    def end_observation(self):
        observed = tuple(self.observed)[1:]
        self.observed[:] = []
        return observed
