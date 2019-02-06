"""Unit tests for pp_highlighter.Styler and pp_highlighter.DummyStyler."""

# pylint: disable=missing-docstring

import unittest

import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from pp_highlighting import dummy_styler, Styler


class TestStyler(unittest.TestCase):
    def test_basic(self):
        styler = Styler()
        integer = styler('class:int', ppc.integer)
        integer.parseString('123', parseAll=True)
        self.assertEqual(styler.get(0), ('class:int', '123'))

    def test_literal(self):
        styler = Styler()
        parser = styler('class:thing', 'hello')
        parser.parseString('hello', parseAll=True)
        self.assertEqual(styler.get(0), ('class:thing', 'hello'))

    def test_clear(self):
        styler = Styler()
        integer = styler('class:int', ppc.integer)
        integer.parseString('123', parseAll=True)
        styler.clear()
        self.assertEqual(styler.get(0), None)

    def test_delete(self):
        styler = Styler()
        integer = styler('class:int', ppc.integer)
        integer.parseString('123', parseAll=True)
        styler.delete(0)
        self.assertEqual(styler.get(0), None)

    def test_delete_no_error(self):
        styler = Styler()
        integer = styler('class:int', ppc.integer)
        integer.parseString('123', parseAll=True)
        self.assertEqual(styler.get(1), None)
        styler.delete(1)

    def test_locs(self):
        styler = Styler()
        parser = pp.OneOrMore(styler('class:int', ppc.integer))
        parser.parseString('123 456', parseAll=True)
        self.assertEqual(styler.locs(), [0, 4])
        self.assertEqual(styler.get(0), ('class:int', '123'))
        self.assertEqual(styler.get(4), ('class:int', '456'))


class TestDummyStyler(unittest.TestCase):
    def test_false(self):
        if dummy_styler:
            self.fail('dummy_styler was not false')

    def test_literal(self):
        parser = dummy_styler('class:thing', 'hello')
        parser.parseString('hello', parseAll=True)
        self.assertEqual(dummy_styler.get(0), None)

    def test_copy(self):
        inner_parser = ppc.integer.copy()
        parser = dummy_styler('class:int', inner_parser)
        def fail():
            self.fail('fail() was called')
        inner_parser.addParseAction(fail)
        parser.parseString('123', parseAll=True)
