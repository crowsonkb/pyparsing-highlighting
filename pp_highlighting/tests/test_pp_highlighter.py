"""Unit tests for pp_highlighting."""

# pylint: disable=missing-docstring

import unittest

from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import FormattedText, PygmentsTokens
from pygments.token import Token
import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from pp_highlighting import PPHighlighter


def parser_factory(styler):
    LPAR, RPAR = map(pp.Suppress, '()')
    a = styler('class:int', ppc.integer)
    b = styler('class:float', ppc.fnumber)
    c = pp.Forward()
    c <<= a ^ b | LPAR + pp.ZeroOrMore(c) + RPAR
    return c


def parser_factory_pygments(styler):
    LPAR, RPAR = map(pp.Suppress, '()')
    a = styler(Token.Number.Integer, ppc.integer)
    b = styler(Token.Number.Float, ppc.fnumber)
    c = pp.Forward()
    c <<= a ^ b | LPAR + pp.ZeroOrMore(c) + RPAR
    return c


def parser_factory_multiclass(styler):
    LPAR, RPAR = map(pp.Suppress, '()')
    a = styler('class:int class:number', ppc.integer)
    b = styler('class:float class:number', ppc.fnumber)
    c = pp.Forward()
    c <<= a ^ b | LPAR + pp.ZeroOrMore(c) + RPAR
    return c


class TestPPHighlighter(unittest.TestCase):
    def test_class(self):
        pph = PPHighlighter(parser_factory)
        fragments = pph.highlight('(1)')
        self.assertTrue(isinstance(fragments, FormattedText))

    def test_single_int(self):
        pph = PPHighlighter(parser_factory)
        fragments = pph.highlight('(1)')
        self.assertEqual(fragments, [('', '('), ('class:int', '1'), ('', ')')])

    def test_preserve_original(self):
        pph = PPHighlighter(parser_factory)
        fragments = pph.highlight('(1.000)')
        self.assertEqual(fragments, [('', '('), ('class:float', '1.000'), ('', ')')])

    def test_tabs(self):
        pph = PPHighlighter(parser_factory)
        fragments = pph.highlight('( \t 1)')
        self.assertEqual(fragments, [('', '( \t '), ('class:int', '1'), ('', ')')])

    def test_newlines(self):
        pph = PPHighlighter(parser_factory)
        fragments = pph.highlight('( \n 1)')
        self.assertEqual(fragments, [('', '( \n '), ('class:int', '1'), ('', ')')])

    def test_html(self):
        pph = PPHighlighter(parser_factory)
        html = pph.highlight_html('(1)')
        expected = '<span class="highlight">(<span class="int">1</span>)</span>'
        self.assertEqual(html, expected)

    def test_html_multiclass(self):
        pph = PPHighlighter(parser_factory_multiclass)
        html = pph.highlight_html('(1)')
        expected = '<span class="highlight">(<span class="int number">1</span>)</span>'
        self.assertEqual(html, expected)

    def test_pygments_class(self):
        pph = PPHighlighter(parser_factory_pygments, pygments_styles=True)
        fragments = pph.highlight('(1)')
        self.assertTrue(isinstance(fragments, PygmentsTokens))

    def test_pygments_tokens(self):
        pph = PPHighlighter(parser_factory_pygments, pygments_styles=True)
        fragments = pph.highlight('(1)')
        self.assertIn(fragments.token_list[1][0], Token.Number.Integer)

    def test_html_pygments(self):
        pph = PPHighlighter(parser_factory_pygments, pygments_styles=True)
        html = pph.highlight_html('(1)')
        expected = '<span class="highlight">(<span class="mi">1</span>)</span>'
        self.assertEqual(html, expected)

    def test_document_lexer(self):
        pph = PPHighlighter(parser_factory)
        lines = pph.lex_document(Document('(1)'))
        self.assertEqual(lines(0), [('', '('), ('class:int', '1'), ('', ')')])

    def test_document_lexer_multiline(self):
        pph = PPHighlighter(parser_factory)
        lines = pph.lex_document(Document('( \n 1)'))
        self.assertEqual(lines(0), [('', '( ')])
        self.assertEqual(lines(1), [('', ' '), ('class:int', '1'), ('', ')')])
        with self.assertRaises(IndexError):
            lines(2)


if __name__ == '__main__':
    unittest.main()
