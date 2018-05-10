from __future__ import absolute_import, division, print_function

from contextlib import contextmanager
from xml.dom.pulldom import (
    parse,
    COMMENT, PROCESSING_INSTRUCTION,
    START_ELEMENT, END_ELEMENT,
    START_DOCUMENT, END_DOCUMENT,
    CHARACTERS, IGNORABLE_WHITESPACE)
from xml.sax.saxutils import XMLGenerator, escape, quoteattr
from xml.sax.xmlreader import AttributesImpl


class XmlReader(object):
    ignored_events = COMMENT, IGNORABLE_WHITESPACE

    def __init__(self, f):
        self.events = iter(parse(f))

    def next(self):
        event = COMMENT
        while event in self.ignored_events:
            event, node = next(self.events, (END_DOCUMENT, None))
        self.event = event
        self.node = node
        return self

    def expect(self, event, name=None):
        if self.event != event:
            raise RuntimeError('expected event %r, but got %r' %
                               (event, self.event))
        if name is not None and self.name != name:
            raise RuntimeError(
                'expected element %r, but got %r' % (name, self.name))

    @property
    def name(self):
        return self.node.nodeName

    @property
    def characters(self):
        return self.node.data

    def attr(self, name):
        node = self.node.getAttributeNode(name)
        return None if node is None else node.value


class XmlWriter(object):
    __slots__ = ['f', 'indent', 'waiting_for_body']

    def __init__(self, f):
        self.f = f
        self.indent = 0
        self.waiting_for_body = False

    def start_document(self):
        self.f.write('<?xml version="1.0" encoding="ISO-8859-1"?>')

    def end_document(self):
        pass

    def ensure_body(self, end='>'):
        if not self.waiting_for_body:
            return False
        self.waiting_for_body = False
        self.f.write(end)
        self.indent += 1
        return True

    def start_element(self, name):
        self.ensure_body()
        self.waiting_for_body = True
        write = self.f.write
        write('\n')
        write('  ' * self.indent)
        write('<')
        write(name)

    def attr(self, name, value):
        if not self.waiting_for_body:
            raise RuntimeError(
                'Opening tag for this element has already been terminated')
        write = self.f.write
        write(' ')
        write(name)
        write('=')
        value = repr(value) if isinstance(value, float) else str(value)
        write(quoteattr(value))

    def end_element(self, name):
        self.indent -= 1
        if self.ensure_body('/>'):
            return
        write = self.f.write
        write('\n')
        write('  ' * self.indent)
        write('</')
        write(name)
        write('>')

    @contextmanager
    def element(self, name):
        self.start_element(name)
        yield
        self.end_element(name)

    def characters(self, s):
        self.ensure_body()
        self.f.write(escape(s))
