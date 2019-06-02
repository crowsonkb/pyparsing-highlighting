"""Unit tests for pp_highlighter.PPHighlighter."""

# pylint: disable=missing-docstring, protected-access, too-many-public-methods

import sys
import unittest

from prompt_toolkit import print_formatted_text
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import FormattedText
import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from pp_highlighting import PPHighlighter


def info(msg):
    print_formatted_text(FormattedText([('ansicyan', msg)]), file=sys.stderr)


try:
    from pygments.token import Token
    info('Pygments is installed; skipping no-Pygments unit tests.')
    HAS_PYGMENTS = True
except ImportError:
    info('Pygments is not installed; skipping Pygments unit tests.')
    HAS_PYGMENTS = False


def parser_factory(styler):
    LPAR, RPAR = map(pp.Suppress, '()')
    a = styler('class:int', ppc.integer)
    b = styler('class:float', ppc.fnumber)
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


def parser_factory_abc(styler):
    a = styler('#f00', 'a')
    b = styler('#00f', 'b')
    return pp.StringStart() + pp.OneOrMore(a | b | 'c')


def parser_factory_htmlescape(styler):
    LANG, RANG = map(pp.Suppress, '<>')
    a = styler('class:int', ppc.integer)
    b = styler('class:float', ppc.fnumber)
    c = pp.Forward()
    c <<= a ^ b | LANG + pp.ZeroOrMore(c) + RANG
    return c


def parser_factory_dotted_classes(styler):
    LPAR, RPAR = map(pp.Suppress, '()')
    a = styler('class:number.int', ppc.integer)
    b = styler('class:number.float', ppc.fnumber)
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


def parser_factory_pygments_subtype(styler):
    LPAR, RPAR = map(pp.Suppress, '()')
    a = styler(Token.Number.Integer.Subtype, ppc.integer)
    b = styler(Token.Number.Float.Subtype, ppc.fnumber)
    c = pp.Forward()
    c <<= a ^ b | LPAR + pp.ZeroOrMore(c) + RPAR
    return c


def parser_factory_backout(styler):
    LPAR, RPAR = map(pp.Suppress, '()')
    a = styler('class:int', ppc.integer) + '='
    b = styler('class:float', ppc.fnumber) + '='
    c = pp.Forward()
    c <<= a ^ b | LPAR + pp.ZeroOrMore(c) + RPAR
    return c


def parser_factory_exception(styler):
    def exception():
        raise RuntimeError('test')
    LPAR, RPAR = map(pp.Suppress, '()')
    a = styler('class:int', ppc.integer)
    a.addParseAction(exception)
    b = styler('class:float', ppc.fnumber)
    c = pp.Forward()
    c <<= a ^ b | LPAR + pp.ZeroOrMore(c) + RPAR
    return c


def parser_factory_overlap(styler):
    LPAR, RPAR = map(pp.Suppress, '()')
    a = styler('class:int', ppc.integer)
    b = styler('class:float', ppc.fnumber)
    c = pp.Forward()
    c <<= a ^ b | LPAR + pp.ZeroOrMore(c) + RPAR
    return styler('bold', c)


def parser_factory_add_parse_action(styler):
    LPAR, RPAR = map(pp.Suppress, '()')
    a = styler('class:int', ppc.integer).addParseAction(lambda t: -t[0])
    b = styler('class:float', ppc.fnumber)
    c = pp.Forward()
    c <<= a ^ b | LPAR + pp.ZeroOrMore(c) + RPAR
    return c


def parser_factory_set_parse_action(styler):
    LPAR, RPAR = map(pp.Suppress, '()')
    a = styler('class:int', ppc.integer).setParseAction(lambda t: -t[0])
    b = styler('class:float', ppc.fnumber)
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

    def test_complex(self):
        pph = PPHighlighter(parser_factory)
        s = '(1 (2 3.00 () 4) 5)'
        pph.expr.parseString(s, parseAll=True)
        fragments = pph.highlight(s)
        expected = [('', '('), ('class:int', '1'), ('', ' ('),
                    ('class:int', '2'), ('', ' '), ('class:float', '3.00'),
                    ('', ' () '), ('class:int', '4'), ('', ') '),
                    ('class:int', '5'), ('', ')')]
        self.assertEqual(fragments, expected)

    def test_adjacent_styled_fragments(self):
        pph = PPHighlighter(parser_factory_abc)
        s = 'aabca'
        pph.expr.parseString(s, parseAll=True)
        fragments = pph.highlight(s)
        expected = [('#f00', 'a'), ('#f00', 'a'), ('#00f', 'b'), ('', 'c'),
                    ('#f00', 'a')]
        self.assertEqual(fragments, expected)

    def test_html(self):
        pph = PPHighlighter(parser_factory)
        html = pph.highlight_html('(1)')
        expected = '<pre class="highlight">(<span class="int">1</span>)</pre>'
        self.assertEqual(html, expected)

    def test_html_wrapping_class(self):
        pph = PPHighlighter(parser_factory)
        html = pph.highlight_html('(1)', css_class='thing')
        expected = '<pre class="thing">(<span class="int">1</span>)</pre>'
        self.assertEqual(html, expected)

    def test_html_multiclass(self):
        pph = PPHighlighter(parser_factory_multiclass)
        html = pph.highlight_html('(1)')
        expected = '<pre class="highlight">(<span class="int number">1</span>)</pre>'
        self.assertEqual(html, expected)

    def test_html_escape(self):
        pph = PPHighlighter(parser_factory_htmlescape)
        html = pph.highlight_html('<1>')
        expected = '<pre class="highlight">&lt;<span class="int">1</span>&gt;</pre>'
        self.assertEqual(html, expected)

    def test_html_dotted_classes(self):
        pph = PPHighlighter(parser_factory_dotted_classes)
        html = pph.highlight_html('(1)')
        expected = '<pre class="highlight">(<span class="number-int">1</span>)</pre>'
        self.assertEqual(html, expected)

    @unittest.skipIf(HAS_PYGMENTS, 'Pygments installed.')
    def test_pygments_not_installed(self):
        with self.assertRaises(ImportError):
            PPHighlighter(parser_factory_pygments, uses_pygments_tokens=True)

    @unittest.skipUnless(HAS_PYGMENTS, 'Pygments not installed.')
    def test_pygments_class(self):
        pph = PPHighlighter(parser_factory_pygments, uses_pygments_tokens=True)
        fragments = pph.highlight('(1)')
        self.assertTrue(isinstance(fragments, FormattedText))

    @unittest.skipUnless(HAS_PYGMENTS, 'Pygments not installed.')
    def test_pygments_tokens(self):
        pph = PPHighlighter(parser_factory_pygments, uses_pygments_tokens=True)
        fragments = pph.highlight('(1)')
        expected = [('class:pygments.text', '('),
                    ('class:pygments.literal.number.integer', '1'),
                    ('class:pygments.text', ')')]
        self.assertEqual(fragments, expected)

    @unittest.skipUnless(HAS_PYGMENTS, 'Pygments not installed.')
    def test_html_pygments(self):
        pph = PPHighlighter(parser_factory_pygments, uses_pygments_tokens=True)
        html = pph.highlight_html('(1)')
        expected = '<pre class="highlight">(<span class="mi">1</span>)</pre>'
        self.assertEqual(html, expected)

    @unittest.skipUnless(HAS_PYGMENTS, 'Pygments not installed.')
    def test_html_pygments_css_class(self):
        pph = PPHighlighter(parser_factory_pygments, uses_pygments_tokens=True)
        html = pph.highlight_html('(1)', css_class='hl')
        expected = '<pre class="hl">(<span class="mi">1</span>)</pre>'
        self.assertEqual(html, expected)

    @unittest.skipUnless(HAS_PYGMENTS, 'Pygments not installed.')
    def test_html_pygments_subtype(self):
        pph = PPHighlighter(parser_factory_pygments_subtype, uses_pygments_tokens=True)
        html = pph.highlight_html('(1)')
        expected = '<pre class="highlight">(<span class="mi">1</span>)</pre>'
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

    def test_restart(self):
        pph = PPHighlighter(parser_factory)
        fragments = pph.highlight('(1 (a 2))')
        expected = [('', '('),
                    ('class:int', '1'),
                    ('', ' (a '),
                    ('class:int', '2'),
                    ('', '))')]
        self.assertEqual(fragments, expected)

    def test_backout(self):
        pph = PPHighlighter(parser_factory_backout)
        fragments = pph.highlight('(1)')
        expected = [('', '(1)')]
        self.assertEqual(fragments, expected)

    def test_warning(self):
        pph = PPHighlighter(parser_factory_exception)
        with self.assertWarns(RuntimeWarning):
            pph.highlight('(1)')

    def test_nonstring_fail(self):
        pph = PPHighlighter(parser_factory)
        with self.assertRaises(TypeError):
            pph.highlight(0)

    def test_overlap(self):
        pph = PPHighlighter(parser_factory_overlap)
        fragments = pph.highlight('(1 2) ')
        self.assertEqual(fragments, [('bold', '(1 2)'), ('', ' ')])

    def test_add_parse_action(self):
        pph = PPHighlighter(parser_factory_add_parse_action)
        fragments = pph.highlight('(1)')
        self.assertEqual(fragments, [('', '('), ('class:int', '1'), ('', ')')])
        result = pph.expr.parseString('(1)', parseAll=True)
        self.assertEqual(result[0], -1)

    def test_set_parse_action(self):
        pph = PPHighlighter(parser_factory_set_parse_action)
        fragments = pph.highlight('(1)')
        self.assertEqual(fragments, [('', '('), ('class:int', '1'), ('', ')')])
        result = pph.expr.parseString('(1)', parseAll=True)
        self.assertEqual(result[0], -1)


if __name__ == '__main__':
    unittest.main()
