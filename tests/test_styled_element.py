"""Unit tests for pp_highlighter.StyledElement."""

# pylint: disable=missing-docstring

import unittest

import pyparsing as pp

from pp_highlighting.pp_highlighter import StyledElement


class TestStyledElement(unittest.TestCase):
    def test_basic(self):
        fragments = {}
        expr = pp.Literal('abc')
        s_expr = StyledElement(fragments, 'class:abc', expr)
        s_expr.parseString('abc', parseAll=True)
        self.assertEqual(list(fragments), [0])
        self.assertEqual(fragments[0], ('class:abc', 'abc'))

    def test_str(self):
        expr = pp.Literal('abc')
        s_expr = StyledElement({}, 'class:abc', expr)
        self.assertEqual(str(expr), str(s_expr))

    def test_does_parse_actions(self):
        fragments = {}
        expr = pp.Word(pp.nums).addParseAction(lambda t: int(t[0]))
        expr.addParseAction(lambda t: t[0] * 2)
        s_expr = StyledElement(fragments, 'class:abc', expr)
        result = s_expr.parseString('123', parseAll=True)[0]
        self.assertEqual(fragments[0], ('class:abc', '123'))
        self.assertEqual(result, 246)


if __name__ == '__main__':
    unittest.main()
