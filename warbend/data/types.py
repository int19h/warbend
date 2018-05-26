from __future__ import absolute_import, division, print_function


def fixed_width_int(n, signed):
    if signed:
        min = -2**(n-1)
        max = 2**(n-1) - 1
    else:
        min = 0
        max = (2**n) - 1

    def decorate(cls):
        def validate(self):
            if not (min <= self <= max):
                raise ValueError('{} is out of range for {}'.format(self, type(self).__name__))
        cls._validate = validate
        return cls
    return decorate


def sbits(n): return fixed_width_int(n, True)


def ubits(n): return fixed_width_int(n, False)


@ubits(8)
class uint8(int):
    __slots__ = []


@ubits(16)
class uint16(int):
    __slots__ = []


@sbits(32)
class int32(int):
    __slots__ = []


@ubits(32)
class uint32(long):
    __slots__ = []


@sbits(64)
class int64(long):
    __slots__ = []


@ubits(64)
class uint64(long):
    __slots__ = []


@ubits(8)
class bool8(uint8):
    __slots__ = []

    def __repr__(self):
        return repr(bool(self))

    def __str__(self):
        return repr(self)


@ubits(32)
class bool32(uint32):
    __slots__ = []

    def __repr__(self):
        return repr(bool(self))

    def __str__(self):
        return repr(self)


class float32(float):
    __slots__ = []

    def __str__(self):
        return repr(self)


class pstr(str):
    __slots__ = []
