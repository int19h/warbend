from __future__ import absolute_import, division, print_function

import bitstruct
from functools import partial
from io import BufferedReader, BufferedWriter
from struct import Struct

from ..data.array import Array, BitArray, is_array, is_bit_array
from ..data.context import Context
from ..data.id_ref import IdRef
from ..data.mutable import path
from ..data.record import Record
from ..data.types import bool8, bool32, float32, int32, int64, pstr, uint8, uint16, uint32, uint64
from ..util.io import source
from ..util.log import INDENT, DEDENT, log_data
from ..util.progress import ProgressBar, ProgressIO

format_name = 'binary'


class Options(object):
    __slots__ = ['report']

    def __init__(self):
        self.report = id

    def copy(self):
        res = Options()
        res.report = self.report
        return res


if log_data:
    def log_write(writer, x):
        log_data('@%08X :: %s = %r\n' % (writer.tell(), type(x).__name__, x))
else:
    log_write = None


def reads(t):
    def decorator(f):
        t._binary_read = staticmethod(f)
        f.__name__ = 'reads(%s)' % t.__name__
        return f
    return decorator


def writes(t):
    def decorator(f):
        t._binary_write = staticmethod(f)
        f.__name__ = 'writes(%s)' % t.__name__
        return f
    return decorator


def read(t, reader, parent, selector, options):
    return t._binary_read(t, reader, parent, selector, options)


def read_as(t):
    return partial(t._binary_read, t)


def write(value, writer, options):
    return type(value)._binary_write(value, writer, options)


def write_as(t):
    return t._binary_write


simple_types = {
    uint8: 'B',
    uint16: 'H',
    int32: 'l',
    uint32: 'L',
    int64: 'q',
    uint64: 'Q',
    float32: 'f',
    bool8: 'B',
    bool32: 'L',
}

for t, fmt in simple_types.iteritems():
    def _(t=t, struct=Struct('=' + fmt)):
        @reads(t)
        def _(t, reader, parent, selector, options):
            data = reader.read(struct.size)
            value, = struct.unpack(data)
            log_data and log_data(value)
            return t(value)

        @writes(t)
        def _(value, writer, options):
            data = struct.pack(value)
            log_write and log_write(writer, value)
            writer.write(data)
    _()


read_int32 = read_as(int32)  # pylint: disable=E1101
write_int32 = write_as(int32)  # pylint: disable=E1101


@reads(pstr)
def _(t, reader, parent, selector, options):
    log_data and log_data('#')
    size = read_int32(reader, parent, selector, options)
    log_data and log_data(' ')
    assert size < 1000000
    value = reader.read(size)
    log_data and log_data(repr(value))
    return pstr(value)


@writes(pstr)
def _(value, writer, options):
    write_int32(len(value), writer, options)
    log_write and log_write(writer, value)
    writer.write(value)


def struct_for(t):
    try:
        struct = t._binary_struct
    except AttributeError:
        fmt = simple_types.get(t.default_type, None)
        struct = Struct('=' + fmt * t.size) if fmt else None
        t._binary_struct = struct
    return struct


@reads(Array)
def _(t, reader, parent, selector, options):
    struct = struct_for(t)
    log_data and log_data('{', INDENT)
    if struct:
        data = reader.read(struct.size)
        array = t(struct.unpack(data), parent=parent, selector=selector)
        log_data and log_data('\n', ', '.join(map(repr, array)))
    else:
        array = t(parent=parent, selector=selector)
        item_type = t.default_type
        for i in range(0, t.size):
            log_data and log_data('\n[%s] ' % i)
            item = read(item_type, reader, array, i, options)
            list.append(array, item)
        array._mark_all_as_dirty()
    log_data and log_data(DEDENT, '\n}')
    return array


@writes(Array)
def _(array, writer, options):
    t = type(array)
    for i, item in enumerate(array):
        assert isinstance(item, t.default_type), path(array, i)
        write(item, writer, options)
    options.report(1)


def bitstruct_for(t):
    try:
        bs = t._binary_bitstruct
    except AttributeError:
        word_count = t.size
        word_size = t.word_size
        fmt = ('u' + str(word_size)) * word_count
        bs = bitstruct.compile(fmt)
        assert bs.calcsize() == word_size * word_count, \
            (bs.calcsize(), word_size, word_count)
        t._binary_bitstruct = bs
    return bs


@reads(BitArray)
def _(t, reader, parent, selector, options):
    data = reader.read(t.word_size * t.size // 8)
    log_data and log_data(('%02X ' * len(data)) %
                          tuple((ord(x) for x in data)))
    words = bitstruct_for(t).unpack(data)
    array = t(words, parent=parent, selector=selector)
    assert len(array) == t.size
    log_data and log_data('{', INDENT)
    i = 0
    for word in array:
        log_data and log_data('\n[%s] %s' % (i, word))
        i += 1
    log_data and log_data(DEDENT, '\n}')
    return array


@writes(BitArray)
def _(array, writer, options):
    t = type(array)
    data = bitstruct_for(t).pack(*array)
    assert len(data) == t.word_size * t.size // 8
    writer.write(data)
    options.report(1)


@reads(Record)
def _(t, reader, parent, selector, options):
    if type(parent) is Context:
        assert not selector
        record = t(context=parent)
    else:
        record = t(parent=parent, selector=selector)
    context = record._context
    log_data and log_data(t.__name__, ' {', INDENT)
    observed = []
    context.begin_observation()

    @record._iter_fields
    def _(fname, ftype):
        observed.extend(context.end_observation())
        log_data and log_data('\n', fname, ' : ', ftype.__name__, ' = ')
        fvalue = read(ftype, reader, record, fname, options)
        assert type(fvalue) is ftype, path(record, fname)
        assert fname not in record._fields, path(record, fname)
        record._fields[fname] = fvalue
        if is_array(fvalue):
            observed.append(fvalue)
        context.begin_observation()

    observed.extend(context.end_observation())
    observed = list({id(obj): obj for obj in observed}.itervalues())
    record._has_observed(observed)
    log_data and log_data(DEDENT, '\n} ', t.__name__)
    return record


@writes(Record)
def _(record, writer, options):
    @record._iter_fields
    def _(fname, ftype):
        assert isinstance(ftype, type)
        fvalue = record[fname]
        assert type(fvalue) is ftype, path(record, fname)
        log_data and log_data(
            fname, ' : ', ftype.__name__, ' = ', fvalue, '\n')
        write(fvalue, writer, options)
    options.report(1)


def load(root_type, reader, options=None):
    options = options.copy() if options else Options()
    context = Context()
    context.source = source(reader)
    with context.transaction, ProgressIO('load', reader) as reader:
        with BufferedReader(reader, 0x1000) as reader:
            g = read(root_type, reader, context, None, options)
            assert reader.read() == b''  # there should be no unparsed data left
    assert not context.transaction.active
    return g


def save(root, writer, options=None):
    options = options.copy() if options else Options()
    report = options.report
    with ProgressBar('save', len(root._context.mutable)) as progress:
        with BufferedWriter(writer, 0x1000) as writer:
            options.report = lambda x: (report(x), progress.report(x))
            return write(root, writer, options)
