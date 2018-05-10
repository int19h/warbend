from __future__ import absolute_import, division, print_function

from ..util.memoize import memoize
from .array import is_array
from .coerce import coerce
from .mutable import Mutable, is_mutable, mutating, path


class Record(Mutable):
    __slots__ = Mutable._slots_required + \
        ['_fields', '_lkg_fields', '_fieldfunc']

    _record_marker = ()

    field_generator = lambda *args: {}

    def __init__(self, **kwargs):
        super(Record, self).__init__(**kwargs)
        self._fields = {}
        self._lkg_fields = []
        self._fieldfunc = None
        self._has_observed((self,))

    def __iter__(self):
        return iter(self._fields.itervalues())

    def __len__(self):
        return len(self._fields)

    def __getitem__(self, name):
        self._has_been_observed()
        return self._fields[name]

    @mutating
    def __setitem__(self, name, value):
        self._fields[name] = value
        if is_array(value):
            self._has_observed((value,))

    @mutating
    def __delitem__(self, name):
        del self._fields[name]

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError()
        else:
            try:
                return self[name]
            except KeyError:
                raise AttributeError()

    def __setattr__(self, name, value):
        try:
            super(Record, self).__setattr__(name, value)
        except AttributeError:
            self[name] = value

    def __delattr__(self, name):
        del self[name]

    def __dir__(self):
        return [fname for fname in self._fields.keys() if not fname.startswith('_')]

    def __call__(self, **kwargs):
        ffunc = self._fieldfunc
        if ffunc is None:
            raise RuntimeError('Must be invoked from a @record function body')
        if len(kwargs) != 1:
            raise ValueError('Single keyword argument required')
        (fname, ftype), = kwargs.viewitems()  # pylint: disable=E0632
        assert isinstance(ftype, type), ftype
        ffunc(fname, ftype)

    def __repr__(self):
        return '<record(%s) at %r>' % (type(self).__name__, self._path)

    @staticmethod
    def _repr_selector(selector):
        return '.' + selector

    def __str__(self):
        fields = ('%s = %s' % (fname, fvalue if is_mutable(fvalue) else repr(fvalue))
                  for fname, fvalue in self._fields.iteritems()
                  if not fname.startswith('_'))
        s = '%s { %s }' % (type(self).__name__, ', '.join(fields))
        return s

    def __index__(self):
        if not is_array(self._parent):
            raise ValueError('%r is not an array item' % self)
        return self._selector

    def _iter_fields(self, fieldfunc):
        f = type(self).field_generator
        try:
            self._fieldfunc = fieldfunc
            f(self)
        finally:
            self._fieldfunc = None

    def _validate(self):
        try:
            assert not self.__dict__, repr(self)
        except AttributeError:
            pass
        fields = self._fields
        funused = set(fields)

        @self._iter_fields
        def _(fname, ftype):
            funused.discard(fname)
            try:
                foldval = fields[fname]
            except KeyError:
                self._invalid_child(fname, 'field is missing')
            fnewval = coerce(self, fname, foldval, ftype)
            if foldval is not fnewval:
                if is_mutable(foldval):
                    foldval._detach()
                fields[fname] = fnewval

        if funused:
            self._invalid_child(funused.pop(), 'unexpected field')
        self._dirty = False

    def _prepare_for_changes(self):
        assert self._context.transaction.active, repr(self)
        if not self._lkg_fields:
            self._lkg_fields[:] = self._fields.items()

    def _commit_changes(self):
        assert self._context.transaction.active, repr(self)
        assert not self._dirty, repr(self)
        del self._lkg_fields[:]

    def _revert_changes(self):
        assert self._context.transaction.active, repr(self)
        if self._lkg_fields:
            self._fields = dict(self._lkg_fields)
            del self._lkg_fields[:]


def is_record(obj):
    return hasattr(type(obj), '_record_marker')


@memoize
def record(f):
    class RecordT(Record):
        __slots__ = []  # suppress __dict__
        field_generator = f
    RecordT.__name__ = f.__name__
    RecordT.__module__ = f.__module__
    return RecordT
