from __future__ import absolute_import, division, print_function

import bitstruct
import operator
import sys

from ..util.foreach import foreach
from ..util.frozendict import frozendict
from ..util.memoize import memoize
from .coerce import coerce
from .enum import simplify_names
from .mutable import Mutable, mutating
from .types import int64


class Array(Mutable, list):
    __slots__ = Mutable._slots_required + ['_lkg_items', '_dirty_indices']

    _array_marker = ()
    size = 0
    singular = None
    keys = {}
    types = {}
    groups = {}
    default_type = type(None)

    def __init__(self, items=(), **kwargs):
        super(Array, self).__init__(items, **kwargs)
        self._lkg_items = []
        self._dirty_indices = set()
        if is_array(items):
            self._observers = items._observers.copy()
        self._mark_all_as_dirty()

    def _prepare_for_changes(self):
        assert self._context.transaction.active, repr(self)
        if not self._lkg_items:
            self._lkg_items[:] = self

    def _commit_changes(self):
        assert self._context.transaction.active, repr(self)
        assert not self._dirty, repr(self)
        del self._lkg_items[:]

    def _revert_changes(self):
        assert self._context.transaction.active, repr(self)
        if self._lkg_items:
            list.__setslice__(self, 0, sys.maxint, self._lkg_items)
            del self._lkg_items[:]

    def _validate(self):
        t = type(self)
        n = len(self)
        if n != t.size:
            self._invalid('{} cannot have {:n} elements.', t.__name__, n)
        foreach(self._validate_item, tuple(self._dirty_indices))
        assert not self._dirty_indices, repr(self)
        self._dirty = False

    def _validate_item(self, index):
        t = type(self)
        itype = t.types.get(index, t.default_type)
        try:
            item = list.__getitem__(self, index)
        except KeyError:
            pass
        else:
            new_item = coerce(self, index, item, itype)
            list.__setitem__(self, index, new_item)
            self._dirty_indices.discard(index)

    def _mark_all_as_dirty(self):
        self._dirty_indices.update(xrange(0, len(self)))

    def __iter__(self):
        self._has_been_observed()
        return super(Array, self).__iter__()

    def __len__(self):
        self._has_been_observed()
        return super(Array, self).__len__()

    def __getitem__(self, index):
        self._has_been_observed()
        try:
            return super(Array, self).__getitem__(index)
        except TypeError:
            t = type(self)
            try:
                index, = [i for i, key in t.keys.iteritems() if key == index]
            except ValueError:
                begin, end = t.groups[index]
                return self[begin:end]
            else:
                return self[index]

    @mutating
    def __setitem__(self, index, value):
        try:
            index = operator.index(index)
        except TypeError:
            t = type(self)
            try:
                index, = [k for k, v in t.keys.iteritems() if v == index]
            except ValueError:
                raise KeyError()
            self[index] = value
            return
        super(Array, self).__setitem__(index, value)
        self._dirty_indices.add(index)

    @mutating
    def __setslice__(self, i, j, iterable):
        i = operator.index(i)
        j = operator.index(j)
        super(Array, self).__setslice__(i, j, iterable)
        self._mark_all_as_dirty()

    @mutating
    def __delitem__(self, *args):
        res = super(Array, self).__delitem__(*args)
        self._mark_all_as_dirty()
        return res

    @mutating
    def __delslice__(self, *args):
        res = super(Array, self).__delslice__(*args)
        self._mark_all_as_dirty()
        return res

    @mutating
    def __iadd__(self, *args):
        res = super(Array, self).__iadd__(*args)
        self._mark_all_as_dirty()
        return res

    @mutating
    def __imul__(self, *args):
        res = super(Array, self).__imul__(*args)
        self._mark_all_as_dirty()
        return res

    def __repr__(self):
        return '<%s at %r>' % (type(self).__name__, self._path)

    @staticmethod
    def _repr_selector(selector):
        return '[%d]' % selector

    def __str__(self):
        t = type(self)
        items = (str(x) for x in self)
        return '%s[%d] { %s }' % (t.default_type.__name__, t.size, ', '.join(items))

    @mutating
    def append(self, *args):
        res = super(Array, self).append(*args)
        self._mark_all_as_dirty()
        return res

    @mutating
    def extend(self, *args):
        res = super(Array, self).extend(*args)
        self._mark_all_as_dirty()
        return res

    @mutating
    def insert(self, *args):
        res = super(Array, self).insert(*args)
        self._mark_all_as_dirty()
        return res

    @mutating
    def remove(self, *args):
        res = super(Array, self).remove(*args)
        self._mark_all_as_dirty()
        return res

    @mutating
    def pop(self, *args):
        res = super(Array, self).pop(*args)
        self._mark_all_as_dirty()
        return res


def is_array(obj):
    return hasattr(type(obj), '_array_marker')


def array(t, size, singular=None, keys=None, types=None, groups=None):
    keys = None if keys is None else frozendict(keys)
    types = None if types is None else frozendict(types)
    return _array(t, size, singular, keys, types, groups)


@memoize
def _array(t, size, singular, keys, types, groups):
    assert isinstance(t, type), t
    assert 0 <= size < 1000000, size

    if issubclass(t, Array):
        raise ValueError('Nested arrays are not supported')

    if singular is None:
        if issubclass(t, Mutable):
            singular = t.__name__
        else:
            singular = '_'
    assert isinstance(singular, str), type(singular)

    keys = simplify_names(keys)

    if types is None:
        types = {}
    assert all(issubclass(itype, t) for itype in types.itervalues()), types

    class ArrayT(Array):
        pass
    ArrayT.__name__ = 'array(%s, %s)' % (t.__name__, size)
    ArrayT.size = size
    ArrayT.singular = singular
    ArrayT.keys = keys
    ArrayT.types = types
    ArrayT.groups = groups
    ArrayT.default_type = t
    return ArrayT


class BitArray(Array):
    _bit_array_marker = ()
    word_size = 0
    default_type = int64

    def __str__(self):
        t = type(self)
        items = (repr(x) for x in self)
        return 'bits[%d * %d] { %s }' % (t.word_size, t.size, ', '.join(items))

    def _validate_item(self, index):
        t = type(self)
        word_max = (1 << t.word_size) - 1
        word = coerce(self, index, self[index], long)
        if not (0 <= word <= word_max):
            self._invalid_child(
                index, 'value {} is out of range [{}..{}]',
                word, 0, word_max)
        list.__setitem__(self, index, t.default_type(word))
        self._dirty_indices.discard(index)


def is_bit_array(obj):
    return hasattr(type(obj), '_bit_array_marker')


def bit_array(word_size, word_count, singular='_', keys=None):
    keys = None if keys is None else frozendict(keys)
    return _bit_array(word_size, word_count, singular, keys)


@memoize
def _bit_array(word_size, word_count, singular, keys):
    assert (word_size * word_count) % 8 == 0, (word_size, word_count)
    assert isinstance(singular, str), type(singular)

    keys = simplify_names(keys)

    class BitArrayT(BitArray):
        pass
    BitArrayT.__name__ = 'bit_array(%s, %s)' % (word_size, word_count)
    BitArrayT.size = word_count
    BitArrayT.word_size = word_size
    BitArrayT.singular = singular
    BitArrayT.keys = keys
    return BitArrayT
