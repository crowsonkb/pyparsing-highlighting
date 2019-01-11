"""Syntax highlighting for prompt_toolkit and HTML with pyparsing."""

import html
import warnings

from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import (FormattedText, PygmentsTokens,
                                           split_lines, to_formatted_text)
from prompt_toolkit.lexers import Lexer
from pygments.token import STANDARD_TYPES, Token
import pyparsing as pp

__all__ = ['dummy_styler', 'PPHighlighter']


class Styler(pp.ParserElement):
    """Saves the original, untokenized text matched by a parse expression as a
    prompt_toolkit text fragment."""
    def __init__(self, fragments, style, expr):
        super().__init__()
        self._fragments = fragments
        self.style = style
        if isinstance(expr, str):
            expr = self._literalStringClass(expr)
        self.expr = expr

    def __str__(self):
        return str(self.expr)

    def parseImpl(self, instring, loc, doActions=True):
        # pylint: disable=protected-access
        end_loc, toks = self.expr._parse(instring, loc, doActions, False)
        self._fragments[loc] = (self.style, instring[loc:end_loc])
        return end_loc, toks


class DummyStyler:
    """A drop-in replacement for :meth:`PPHighlighter.styler` which merely
    returns a copy of the given parse expression without capturing text or
    applying styles. To simplify testing whether a parser factory has been
    passed :func:`dummy_styler`, :code:`bool(dummy_styler)` is `False`.

    Args:
        style (Union[str, pygments.token.Token]): Ignored.
        expr (Union[str, pyparsing.ParserElement]): Copied, unless it is a
            string literal, in which case it will be wrapped by
            :attr:`pyparsing.ParserElement._literalStringClass` (default
            :class:`pyparsing.Literal`).

    Returns:
        pyparsing.ParserElement: A copy of the input parser element.
    """
    def __bool__(self):
        return False

    def __call__(self, style, expr):
        if isinstance(expr, str):
            # pylint: disable=protected-access
            return pp.ParserElement._literalStringClass(expr)
        return expr.copy()

    def __repr__(self):
        return '<{.__module__}.dummy_styler(style, expr)>'.format(self)

dummy_styler = DummyStyler()


class PPHighlighter(Lexer):
    """Syntax highlighting for prompt_toolkit and HTML with pyparsing.

    This class can be used to highlight text via its :meth:`highlight` method
    (for :func:`prompt_toolkit.print_formatted_text`—see `the prompt_toolkit
    documentation
    <https://python-prompt-toolkit.readthedocs.io/en/stable/pages/printing_text.html#>`_
    for details), its :meth:`highlight_html` method, and by passing it as the
    `lexer` argument to a :class:`prompt_toolkit.PromptSession`.
    """

    def __init__(self, parser_factory, *, pygments_styles=False):
        """Constructs a new :class:`PPHighlighter`.

        You should supply a parser factory, a function that takes one argument
        and returns a parse expression. :class:`PPHighlighter` will pass its
        :meth:`styler` method as the argument (see :meth:`styler` for more
        details). :meth:`styler` modifies parse expressions to capture and style
        the text they match. The `style` argument to :meth:`styler` can be
        either a prompt_toolkit style string or a Pygments token.

        Examples:

            >>> def parser_factory(styler):
            >>>     a = styler('class:int', ppc.integer)
            >>>     return pp.delimitedList(a)
            >>> pph = PPHighlighter(parser_factory)
            >>> pph.highlight('1, 2, 3')
            FormattedText([('class:int', '1'), ('', ', '), ('class:int', '2'),
            ('', ', '), ('class:int', '3')])

            :class:`FormattedText` instances can be passed to
            :func:`prompt_toolkit.print_formatted_text`.

        Args:
            parser_factory (Callable[[Callable], pyparsing.ParserElement]): The
                parser factory.
            pygments_styles (bool): Whether or not the parser is styled using
                Pygments tokens.
        """
        self._fragments = {}
        self._pygments_styles = pygments_styles
        self._parser = parser_factory(self.styler)
        self._parser.parseWithTabs()

    def __repr__(self):
        return '{0.__class__.__name__}({0._parser!r})'.format(self)

    def styler(self, style, expr):
        """Wraps a pyparsing parse expression to capture text fragments.

        :meth:`styler` wraps the given parse expression, capturing the original
        text it matched, and returns the modified parse expression. The `style`
        argument can be either a prompt_toolkit style string or a Pygments
        token.

        Args:
            style (Union[str, pygments.token.Token]): The style to set for this
                text fragment, as a string or a Pygments token.
            expr (Union[str, pyparsing.ParserElement]): The pyparsing parser to
                wrap. If a literal string is specified, it will be wrapped by
                :attr:`pyparsing.ParserElement._literalStringClass` (default
                :class:`pyparsing.Literal`).

        Returns:
            pyparsing.ParserElement: The wrapped parser.
        """
        return Styler(self._fragments, style, expr)

    def _scan_string(self, s):
        """Runs the parser over the input string, capturing styled text.

        Adapted from :meth:`pyparsing.ParserElement.scanString` for custom
        exception handling.
        """
        if not self._parser.streamlined:
            self._parser.streamline()
        for e in self._parser.ignoreExprs:
            e.streamline()

        loc = 0
        preloc = None
        pp.ParserElement.resetCache()
        while loc <= len(s):
            try:
                preloc = self._parser.preParse(s, loc)
                # pylint: disable=protected-access
                nextloc, _ = self._parser._parse(s, preloc, callPreParse=False)
            except Exception as err:  # pylint: disable=broad-except
                if preloc is None:
                    raise
                loc = preloc + 1
                if not isinstance(err, pp.ParseBaseException):
                    msg = 'Exception during parsing: {0.__class__.__name__}: {0}'
                    warnings.warn(msg.format(err), RuntimeWarning)
            else:
                loc = nextloc if nextloc > loc else preloc + 1

    def _highlight(self, s):
        """Gathers captured styled text and intervening unstyled text into a
        :class:`FormattedText` instance."""
        if not isinstance(s, str):
            msg = 'Cannot highlight type {}, only str.'
            raise TypeError(msg.format(type(s).__name__))

        default_style = Token.Text if self._pygments_styles else ''

        self._fragments.clear()
        self._scan_string(s)
        locs = sorted(self._fragments)
        locs.append(len(s))

        i = 0
        loc = 0
        fragments = FormattedText()
        while loc < len(s):
            fragment = self._fragments.get(loc)
            if fragment:
                fragments.append(fragment)
                loc += len(fragment[1])
                while locs[i] < loc:
                    i += 1
            else:
                fragments.append((default_style, s[loc:locs[i]]))
                loc = locs[i]

        return fragments

    def highlight(self, s):
        """Highlights a string, returning a list of fragments suitable for
        :func:`prompt_toolkit.print_formatted_text`.

        Args:
            s (str): The input string.

        Returns:
            FormattedText: The resulting list of prompt_toolkit text fragments.
        """
        fragments = self._highlight(s)
        if self._pygments_styles:
            return to_formatted_text(PygmentsTokens(fragments))
        return fragments

    def print(self, *values, **kwargs):
        """::

            print(*values, sep=' ', end='\\n', file=None, flush=False,
                  style=None, output=None, color_depth=None,
                  style_transformation=None, include_default_pygments_style=None)

        Highlights and prints the values to a stream, or to `sys.stdout` by
        default. It calls :func:`prompt_toolkit.print_formatted_text` internally
        and takes the same keyword arguments as it (compatible with the builtin
        :func:`print`).
        """
        print_formatted_text(*map(self.highlight, map(str, values)), **kwargs)

    @classmethod
    def _pygments_css_class(cls, token):
        """Returns the standard CSS class name for a Pygments token."""
        try:
            return STANDARD_TYPES[token]
        except KeyError:
            return cls._pygments_css_class(token.parent)

    def highlight_html(self, s):
        """Highlights a string, returning HTML.

        Only CSS class names are currently supported. Parts of the style string
        that do not begin with ``class:`` will be ignored. If there are dots
        in the class name, they will be turned into hyphens.

        Args:
            s (str): The input string.

        Returns:
            str: The generated HTML.
        """
        fragments = self._highlight(s)
        tags = ['<span class="highlight">']
        template = '<span class="{}">{}</span>'
        table = str.maketrans({'.': '-'})
        for style, text in fragments:
            classes = []
            if self._pygments_styles:
                classes.append(self._pygments_css_class(style))
            else:
                for st in style.split():
                    if st.startswith('class:'):
                        classes.append(html.escape(st[6:].translate(table)))
            if classes and classes[0]:
                tags.append(template.format(' '.join(classes), html.escape(text)))
            else:
                tags.append(html.escape(text))
        tags.append('</span>')
        return ''.join(tags)

    def lex_document(self, document):
        lines = list(split_lines(self.highlight(document.text)))
        return lambda i: lines[i]
