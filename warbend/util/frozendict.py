from __future__ import absolute_import, division, print_function

import collections
import operator
import functools
import sys


class frozendict(collections.Mapping):
    __slots__ = ['_dict', '_hash']

    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)
        self._hash = None

    def __getitem__(self, key):
        return self._dict[key]

    def __contains__(self, key):
        return key in self._dict

    def copy(self, **add_or_replace):
        return type(self)(self, **add_or_replace)

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self._dict)

    def __eq__(self, other):
        if isinstance(other, frozendict):
            return self._dict == other._dict
        return super(frozendict, self).__eq__(other)

    def __hash__(self):
        h = self._hash
        if h is None:
            h = hash(tuple(self._dict.items()))
            self._hash = h
        return h

    def items(self):
        return self._dict.items()

    def iteritems(self):
        return self._dict.iteritems()

    def keys(self):
        return self._dict.keys()

    def iterkeys(self):
        return self._dict.iterkeys()

    def itervalues(self):
        return self._dict.itervalues()
