from __future__ import absolute_import, division, print_function

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
    assert isinstance(t, type), t
    assert len(names) > 0

    class EnumT(Enum, t):
        pass
    EnumT.__name__ = 'enum(%s)' % t.__name__
    EnumT.base_type = t
    EnumT.names = simplify_names(names)
    return EnumT
