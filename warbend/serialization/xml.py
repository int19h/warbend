from __future__ import absolute_import, division, print_function

from functools import partial
from io import BufferedReader, BufferedWriter
import struct

from ..data.array import Array, is_array
from ..data.context import Context
from ..data.enum import Enum
from ..data.mutable import path
from ..data.record import Record
from ..data.types import bool8, float32, int32, int64, pstr, uint8, uint16, uint32, uint64
from ..util.io import source
from ..util.log import INDENT, DEDENT, log_data
from ..util.progress import ProgressBar, ProgressIO
from ..util.xml import XmlReader, XmlWriter, START_DOCUMENT, END_DOCUMENT, START_ELEMENT, END_ELEMENT, CHARACTERS

format_name = 'XML'


class Options(object):
    __slots__ = ['decorate', 'report']

    def __init__(self):
        self.decorate = False
        self.report = id

    def copy(self):
        res = Options()
        res.decorate = self.decorate
        res.report = self.report
        return res


def reads(t):
    def decorator(f):
        t._xml_read = staticmethod(f)
        f.__name__ = 'reads(%s)' % t.__name__
        return f
    return decorator


def writes(t):
    def decorator(f):
        t._xml_write = staticmethod(f)
        f.__name__ = 'writes(%s)' % t.__name__
        return f
    return decorator


def read_as(t):
    return partial(t._xml_read, t)
    

def write_as(t):
    return t._xml_write


def read(t, reader, parent, selector, options):
    return t._xml_read(t, reader, parent, selector, options)


def write(value, writer, options):
    return write_as(type(value))(value, writer, options)


simple_types = {
    uint8,
    uint16,
    int32,
    uint32,
    int64,
    uint64,
    float32,
    bool8,
    pstr,
}

for t in simple_types:
    def _(t=t):
        @reads(t)
        def _(t, reader, parent, selector, options):
            value = reader.attr('_')
            log_data and log_data(value)
            reader.next().expect(END_ELEMENT)
            return t(value)

        @writes(t)
        def _(value, writer, options):
            writer.attr('_', str(value))
    _()


float32_struct = struct.Struct('=f')
uint32_struct = struct.Struct('=L')


@reads(float32)
def _(t, reader, parent, selector, options):
    s = reader.attr('_')
    value = float32(s)
    log_data and log_data(repr(value))
    raw_s = reader.attr('_r')
    if raw_s:
        raw = long(raw_s, 16)
        value_via_raw, = float32_struct.unpack(uint32_struct.pack(raw))
        if str(value) != str(value_via_raw):
            raise ValueError('floating point mismatch between _="%s" (%s) and _raw="%s" (%s)' %
                             (s, value, raw_s, value_via_raw))
        value = value_via_raw
    reader.next().expect(END_ELEMENT)
    return t(value)


@writes(float32)
def _(value, writer, options):
    s = str(value)
    writer.attr('_', s)
    raw = float32_struct.pack(value)
    raw_via_str = float32_struct.pack(float32(s))
    if raw != raw_via_str:
        writer.attr('_r', '%08X' % uint32_struct.unpack(raw))


@writes(Enum)
def _(value, writer, options):
    t = type(value)
    write_as(t.base_type)(value, writer, options)
    if options.decorate:
        try:
            name = t.names[value]
        except KeyError:
            pass
        else:
            writer.attr('_e', name)


@reads(Array)
def _(t, reader, parent, selector, options):
    log_data and log_data('{', INDENT)
    array = t(parent=parent, selector=selector)
    item_type = t.default_type
    for i in range(0, t.size):
        log_data and log_data('\n[%s] ' % i)
        reader.next().expect(START_ELEMENT)
        item = read(item_type, reader, array, i, options)
        reader.expect(END_ELEMENT)
        list.append(array, item)
    reader.next().expect(END_ELEMENT)
    log_data and log_data(DEDENT, '\n}')
    return array


@writes(Array)
def _(array, writer, options):
    t = type(array)
    tagfmt = '_%%0%dd' % len(str(len(array) - 1))
    for i, item in enumerate(array):
        assert isinstance(item, t.default_type), path(array, i)
        tag = t.keys.get(i, tagfmt % i)
        with writer.element(tag):
            write(item, writer, options)
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

        reader.next().expect(START_ELEMENT, fname)
        fvalue = read(ftype, reader, record, fname, options)
        reader.expect(END_ELEMENT)

        assert type(fvalue) is ftype, path(record, fname)
        assert fname not in record._fields, path(record, fname)
        record._fields[fname] = fvalue
        if is_array(fvalue):
            observed.append(fvalue)
        context.begin_observation()

    reader.next().expect(END_ELEMENT)
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
        log_data and log_data(fname, ' : ',
                              ftype.__name__, ' = ', fvalue, '\n')
        with writer.element(fname):
            write(fvalue, writer, options)
    options.report(1)


def load(root_type, reader, options=None):
    options = options or Options()
    context = Context()
    context.source = source(reader)
    with context.transaction:
        with ProgressIO('load', reader) as reader:
            with BufferedReader(reader, 0x1000) as reader:
                reader = XmlReader(reader)
                reader.ignored_events += (CHARACTERS,)
                reader.next().expect(START_DOCUMENT)
                reader.next().expect(START_ELEMENT, root_type.__name__)
                g = read(root_type, reader, context, None, options)
                reader.expect(END_ELEMENT)
                reader.next().expect(END_DOCUMENT)
    assert not context.transaction.active
    return g


def save(root, writer, options=None):
    options = options.copy() if options else Options()
    report = options.report
    with BufferedWriter(writer, 0x1000) as writer:
        with ProgressBar('save', len(root._context.mutable)) as progress:
            options.report = lambda x: (report(x), progress.report(x))
            writer = XmlWriter(writer)
            writer.start_document()
            with writer.element(type(root).__name__):
                return write(root, writer, options)
            writer.end_document()
