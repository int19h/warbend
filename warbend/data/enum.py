from __future__ import absolute_import, division, print_function

from numbers import Integral
import operator
from os.path import commonprefix

from ..util.frozendict import frozendict
from ..util.memoize import memoize


@memoize
def simplify_names(names):
    if not names:
        return {}
    cp = commonprefix(set(names.itervalues()) - {None})
    if not cp:
        return names
    res = {}
    for index, name in names.iteritems():
        res[index] = name[len(cp):]
    return res


class Enum(object):
    names = {}
    base_type = type(None)

    def __repr__(self):
        try:
            name = type(self).names[self]
        except KeyError:
            name = None
        return str(name or self)


def enum(t, names):
    return _enum(t, frozendict(names))


@memoize
def _enum(t, names):
    assert issubclass(t, Integral), t
    assert len(names) > 0

    class EnumT(Enum, t):
        pass
    EnumT.__name__ = 'enum(%s)' % t.__name__
    EnumT.base_type = t
    EnumT.names = simplify_names(names)
    return EnumT


class Flags(Enum):
    names = {}
    base_type = type(None)

    def __repr__(self):
        s = self
        fs = {flag: name for flag, name in self.names.iteritems()
              if (self & flag) == flag}
        if fs:
            if 0 in fs:
                if self == 0:
                    fs = {0: fs[0]}
                else:
                    del fs[0]
            x = reduce(operator.or_, fs.iterkeys(), 0)
            if x == self:
                s = '|'.join(fs.itervalues())
        return "(%s)" % s


def flags(t, names):
    return _flags(t, frozendict(names))


@memoize
def _flags(t, names):
    assert issubclass(t, Integral), t
    assert len(names) > 0

    class FlagsT(Flags, t):
        pass
    FlagsT.__name__ = 'flags(%s)' % t.__name__
    FlagsT.base_type = t
    FlagsT.names = simplify_names(names)
    return FlagsT