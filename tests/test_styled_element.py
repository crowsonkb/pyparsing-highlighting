"""Unit tests for pp_highlighter.StyledElement."""

# pylint: disable=missing-docstring, protected-access, too-many-public-methods

import unittest

import pyparsing as pp

from pp_highlighting.pp_highlighter import StyledElement


class TestStyledElement(unittest.TestCase):
    def test_basic(self):
        s = 'abc'
        fragments = {}
        style = 'class:abc'
        expr = pp.Literal(s)
        s_expr = StyledElement(fragments, style, expr)
        s_expr.parseString(s, parseAll=True)
        self.assertEqual(list(fragments), [0])
        self.assertEqual(fragments[0], (style, s))


if __name__ == '__main__':
    unittest.main()
