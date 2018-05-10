from __future__ import absolute_import, division, print_function

import operator

from .. import mode
from ..util.io import eprintf
from .errors import ValidationError
from .coerce import no_coerce_warnings
from .context import Context


class Mutable(object):
    _mutable_marker = ()

    __slots__ = ['_context', '_parent', '_selector', '_observers', '_dirty']
    _slots_required = __slots__
    __slots__ = []

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        selector = kwargs.pop('selector', type(self).__name__)
        context = kwargs.pop('context', None)
        assert (parent is None) ^ (context is None)
        if parent is not None:
            assert context is None, path(parent, selector)
            assert is_mutable(parent)
            context = parent._context
        super(Mutable, self).__init__(*args, **kwargs)
        self._context = context
        self._parent = parent
        self._selector = selector
        self._observers = {}
        self._dirty = True
        context.mutable[id(self)] = self

    @property
    def _root(self):
        obj = self
        while obj._parent is not None:
            obj = obj._parent
        return obj

    @property
    def _path(self):
        parent = self._parent
        selector = self._selector
        if parent:
            return parent._path + type(parent)._repr_selector(selector)
        else:
            return selector

    @staticmethod
    def _repr_selector(selector):
        raise NotImplementedError()

    def _detach(self):
        del self._context.mutable[id(self)]
        self._context = None
        self._observers.clear()

    def _has_observed(self, others):
        for other in others:
            assert is_mutable(other), type(other)
            other._observers[id(self)] = self

    def _has_been_observed(self):
        self._context.observe(self)

    def _prepare_for_changes(self):
        raise NotImplementedError()

    def _validate(self):
        raise NotImplementedError()

    def _invalid(self, because, *args):
        raise ValidationError(path(self), because.format(*args))

    def _invalid_child(self, selector, because, *args):
        raise ValidationError(path(self, selector), because.format(*args))

    def _commit_changes(self):
        pass

    def _revert_changes(self):
        pass


def is_mutable(obj):
    return hasattr(obj, '_mutable_marker')


def mutating(f):
    def g(self, *args, **kwargs):
        transaction = self._context.transaction
        was_active = transaction.active
        transaction.begin(automatic=True)
        self._prepare_for_changes()
        self._dirty = True
        try:
            return f(self, *args, **kwargs)
        finally:
            try:
                transaction.commit()
            except Exception:
                if transaction.is_automatic:
                    if mode.is_interactive:
                        eprintf('Failed to validate, reverting changes ... ')
                    transaction.rollback()
                    if mode.is_interactive:
                        eprintf('done!\n')
                raise
            finally:
                assert transaction.active == was_active
    return g


def path(obj, selector=None):
    if not is_mutable(obj):
        raise ValueError()
    s = obj._path
    if selector is not None:
        s += obj._repr_selector(selector)
    return s


def parent(obj):
    if not is_mutable(obj):
        raise ValueError()
    return obj._parent


def selector(obj):
    if not is_mutable(obj):
        raise ValueError()
    return obj._selector


def root(obj):
    if not is_mutable(obj):
        raise ValueError()
    return obj._root


def transaction(mutable):
    return mutable._context.transaction
