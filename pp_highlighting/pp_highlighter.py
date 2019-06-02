"""Syntax highlighting for prompt_toolkit and HTML with pyparsing."""

import html
import io
import sys
import warnings

from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import (FormattedText, PygmentsTokens,
                                           split_lines, to_formatted_text)
from prompt_toolkit.output.vt100 import Vt100_Output
from prompt_toolkit.lexers import Lexer
import pyparsing as pp

try:
    from pygments.token import STANDARD_TYPES, Token
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False

__all__ = ['DummyStyler', 'PPHighlighter', 'Styler']

Vt100_Output._fds_not_a_terminal.add(None)  # pylint: disable=protected-access


class StyledElement(pp.ParserElement):
    """Saves the original, untokenized text matched by a parse expression as a
    prompt_toolkit text fragment."""

    def __init__(self, fragments, style, expr):
        super().__init__()
        self._fragments = fragments
        self.style = style
        self.expr = expr

    def __str__(self):
        return str(self.expr)

    def parseImpl(self, instring, loc, doActions=True):
        # pylint: disable=protected-access
        end_loc, toks = self.expr._parse(instring, loc, doActions, False)
        self._fragments[loc] = (self.style, instring[loc:end_loc])
        return end_loc, toks


class Styler:
    """Wraps pyparsing parse expressions to capture styled text fragments."""

    def __init__(self):
        self.fragments = {}

    def __call__(self, style, expr):
        """Wraps the given parse expression to capture the original text it
        matched, and returns the modified parse expression. The `style` argument
        can be either a prompt_toolkit style string or a Pygments token.

        Args:
            style (Union[pygments.token.Token, str]): The style to set for this
                text fragment, as a string or a Pygments token.
            expr (Union[pyparsing.ParserElement, str]): The pyparsing parser to
                wrap. If a literal string is specified, it will be wrapped by
                :attr:`pyparsing.ParserElement._literalStringClass` (default
                :class:`pyparsing.Literal`).

        Returns:
            pyparsing.ParserElement: The wrapped parser.
        """
        if isinstance(expr, str):
            # pylint: disable=protected-access
            expr = pp.ParserElement._literalStringClass(expr)
        return StyledElement(self.fragments, style, expr)

    def clear(self):
        """Removes all captured styled text fragments."""
        self.fragments.clear()

    def delete(self, loc):
        """Removes the styled text fragment starting at a given location if it
        exists.

        Args:
            loc (int): The styled text fragment to delete's start location.
        """
        self.fragments.pop(loc, None)

    def get(self, loc):
        """Returns the styled text fragment starting at a given location if it
        exists, else `None`.

        Args:
            loc (int): The styled text fragment's start location.

        Returns:
            Optional[Tuple[Union[pygments.token.Token, str], str]]: The styled
            text fragment, if it exists.
        """
        return self.fragments.get(loc)

    def locs(self):
        """Returns a sorted list of styled text start locations.

        Returns:
            List[int]: A sorted list of styled text start locations.
        """
        return sorted(self.fragments)


class DummyStyler(Styler):
    """A drop-in replacement for :class:`Styler` which, when called, merely
    returns a copy of the given parse expression without capturing text or
    applying styles. To aid in testing whether a parser factory has been passed
    a :class:`DummyStyler` object, :code:`bool(DummyStyler())` is `False`.
    """

    def __bool__(self):
        return False

    def __call__(self, style, expr):
        """Returns a copy of the given parse expression.

        Args:
            style (Union[pygments.token.Token, str]): Ignored.
            expr (Union[pyparsing.ParserElement, str]): Copied, unless it is a
                string literal, in which case it will be wrapped by
                :attr:`pyparsing.ParserElement._literalStringClass` (default
                :class:`pyparsing.Literal`).

        Returns:
            pyparsing.ParserElement: A copy of the input parse expression.
        """
        if isinstance(expr, str):
            # pylint: disable=protected-access
            return pp.ParserElement._literalStringClass(expr)
        return expr.copy()


class PPHighlighter(Lexer):
    """Syntax highlighting for prompt_toolkit and HTML with pyparsing.

    This class can be used to highlight text via its :meth:`highlight` method
    (for :func:`prompt_toolkit.print_formatted_text`—see `the prompt_toolkit
    documentation
    <https://python-prompt-toolkit.readthedocs.io/en/stable/pages/printing_text.html#>`_
    for details), its :meth:`highlight_html` method, its :meth:`print` method,
    and by passing it as the `lexer` argument to a
    :class:`prompt_toolkit.PromptSession`.
    """

    def __init__(self, parser_factory, *, uses_pygments_tokens=False):
        """Constructs a new :class:`PPHighlighter`.

        You should supply a parser factory, a function that takes one argument
        and returns a parse expression. :class:`PPHighlighter` will pass a
        :class:`Styler` object as the argument (see :class:`Styler` for more
        details).

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
            parser_factory (Callable[[Styler], pyparsing.ParserElement]): The
                parser factory.
            uses_pygments_tokens (bool): Whether or not the parser is styled
                using Pygments tokens.

        Raises:
            ImportError: If `uses_pygments_tokens` is `True` and Pygments is
                not installed.
        """
        self.styler = Styler()
        if uses_pygments_tokens and not HAS_PYGMENTS:
            raise ImportError('Pygments must be installed to use Pygments tokens.')
        self.uses_pygments_tokens = uses_pygments_tokens
        self.expr = parser_factory(self.styler)
        self.expr.parseWithTabs()

    def __repr__(self):
        return '{0.__class__.__name__}({0.expr!r})'.format(self)

    def _scan_string(self, s):
        """Runs the parser over the input string, capturing styled text.

        Adapted from :meth:`pyparsing.ParserElement.scanString` for custom
        exception handling.
        """
        if not self.expr.streamlined:
            self.expr.streamline()
        for e in self.expr.ignoreExprs:
            e.streamline()

        loc = 0
        preloc = None
        pp.ParserElement.resetCache()
        while loc <= len(s):
            try:
                preloc = self.expr.preParse(s, loc)
                # pylint: disable=protected-access
                nextloc, _ = self.expr._parse(s, preloc, callPreParse=False)
            except Exception as err:  # pylint: disable=broad-except
                if preloc is None:
                    raise
                self.styler.delete(preloc)
                loc = preloc + 1
                if not isinstance(err, pp.ParseBaseException):
                    msg = 'Exception during parsing: {0.__class__.__name__}: {0}'
                    warnings.warn(msg.format(err), RuntimeWarning)
            else:
                loc = nextloc if nextloc > loc else preloc + 1

    def _highlight(self, s):
        """Gathers captured styled text and intervening unstyled text into a
        :class:`prompt_toolkit.formatted_text.FormattedText` instance."""
        if not isinstance(s, str):
            msg = 'Cannot highlight type {}, only str.'
            raise TypeError(msg.format(type(s).__name__))

        default_style = Token.Text if self.uses_pygments_tokens else ''

        self.styler.clear()
        self._scan_string(s)
        locs = self.styler.locs()
        locs.append(len(s))

        i = 0
        loc = 0
        fragments = FormattedText()
        while loc < len(s):
            fragment = self.styler.get(loc)
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
            prompt_toolkit.formatted_text.FormattedText: The resulting list of
            prompt_toolkit text fragments.
        """
        fragments = self._highlight(s)
        if self.uses_pygments_tokens:
            return to_formatted_text(PygmentsTokens(fragments))
        return fragments

    def lex_document(self, document):
        lines = list(split_lines(self.highlight(document.text)))
        return lambda i: lines[i]

    @classmethod
    def _pygments_css_class(cls, token):
        """Returns the standard CSS class name for a Pygments token."""
        try:
            return STANDARD_TYPES[token]
        except KeyError:
            return cls._pygments_css_class(token.parent)

    def highlight_html(self, s, *, css_class='highlight'):
        """Highlights a string, returning HTML.

        Only CSS class names are currently supported. Parts of the style string
        that do not begin with ``class:`` will be ignored. If there are dots
        in the class name, they will be turned into hyphens.

        Args:
            s (str): The input string.
            css_class (str): The CSS class for the wrapping tag.

        Returns:
            str: The generated HTML.
        """
        fragments = self._highlight(s)
        tags = ['<pre class="{}">'.format(css_class)]
        template = '<span class="{}">{}</span>'
        table = str.maketrans({'.': '-'})
        for style, text in fragments:
            classes = []
            if self.uses_pygments_tokens:
                classes.append(self._pygments_css_class(style))
            else:
                for st in style.split():
                    if st.startswith('class:'):
                        classes.append(html.escape(st[6:].translate(table)))
            if classes and classes[0]:
                tags.append(template.format(' '.join(classes),
                                            html.escape(text)))
            else:
                tags.append(html.escape(text))
        tags.append('</pre>')
        return ''.join(tags)

    def print(self, *values, file=sys.stdout, **kwargs):
        """Highlights and prints the values to a stream, or to `sys.stdout` by
        default. It calls :func:`prompt_toolkit.print_formatted_text` internally
        and takes the same keyword arguments as it (compatible with the builtin
        :func:`print`).

        Default values of keyword-only arguments::

            print(*values, sep=' ', end='\\n', file=sys.stdout, flush=False,
                  style=None, output=None, color_depth=None,
                  style_transformation=None, include_default_pygments_style=None)
        """
        # Monkey patch non-tty file objects for compatibility
        if file is not None:
            try:
                file.fileno()
            except io.UnsupportedOperation:
                file.fileno = lambda: None
            if not hasattr(file, 'encoding'):
                file.encoding = ''

        print_formatted_text(*map(lambda s: self.highlight(str(s)), values),
                             file=file, **kwargs)
