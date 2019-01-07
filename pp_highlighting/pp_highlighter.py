"""Syntax highlighting with pyparsing."""

import html
from warnings import warn

from prompt_toolkit.formatted_text import (FormattedText, PygmentsTokens,
                                           split_lines, to_formatted_text)
from prompt_toolkit.lexers import Lexer
from pygments.token import STANDARD_TYPES, Token
import pyparsing as pp

__all__ = ['PPHighlighter']


class PPHighlighter(Lexer):
    """Syntax highlighting with pyparsing.

    This class can be used to highlight text via its :meth:`highlight` method
    (for :func:`prompt_toolkit.print_formatted_text`), its
    :meth:`highlight_html` method, and by passing it as the `lexer` argument to
    a :class:`prompt_toolkit.PromptSession`.
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

    def styler(self, style, expr):
        """Wraps a pyparsing parse expression to capture text fragments.

        :meth:`styler` wraps the given parse expression in
        :func:`pyparsing.originalTextFor` to capture the original text it
        matched, and returns the modified parse expression. You must add parse
        actions to the modified parse expression with :meth:`addParseAction`
        instead of :meth:`setParseAction`, or it will stop capturing text. The
        `style` argument can be either a prompt_toolkit style string or a
        Pygments token.

        Args:
            style (Union[str, pygments.token.Token]): The style to set for this
                text fragment, as a string or a Pygments token.
            expr (pyparsing.ParserElement): The pyparsing parser to wrap.

        Returns:
            pyparsing.ParserElement: The wrapped parser.
        """
        def action(s, loc, toks):
            text = s[toks['_original_start']:toks['_original_end']]
            self._fragments[loc] = (style, text)
            return toks[1:-1]
        new_expr = pp.originalTextFor(expr)
        new_expr.setParseAction(action)
        return new_expr

    # pylint: disable=protected-access
    def _scan_string(self, s):
        """Adapted from :meth:`pyparsing.ParserElement.scanString` for custom
        exception handling."""
        if not self._parser.streamlined:
            self._parser.streamline()
        for e in self._parser.ignoreExprs:
            e.streamline()

        loc = 0
        pp.ParserElement.resetCache()
        while loc <= len(s):
            try:
                preloc = self._parser.preParse(s, loc)
                nextloc, _ = self._parser._parse(s, preloc, callPreParse=False)
            except Exception as err:  # pylint: disable=broad-except
                loc = preloc + 1
                if not isinstance(err, pp.ParseBaseException):
                    msg = 'Exception during parsing: {}: {}'
                    warn(msg.format(type(err).__name__, err), RuntimeWarning)
            else:
                loc = nextloc if nextloc > loc else preloc + 1

    def _highlight(self, s):
        default_style = Token.Text if self._pygments_styles else ''

        self._fragments = {}
        self._scan_string(s)

        fragments = FormattedText()
        i = 0
        unstyled_text = []
        while i < len(s):
            if i in self._fragments:
                if unstyled_text:
                    fragments.append((default_style, ''.join(unstyled_text)))
                    unstyled_text = []
                fragment = self._fragments[i]
                fragments.append(fragment)
                i += len(fragment[1])
            else:
                unstyled_text.append(s[i])
                i += 1
        if unstyled_text:
            fragments.append((default_style, ''.join(unstyled_text)))

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

    @classmethod
    def _pygments_css_class(cls, token):
        try:
            return STANDARD_TYPES[token]
        except KeyError:
            return cls._pygments_css_class(token.parent)

    def highlight_html(self, s):
        """Highlights a string, returning HTML.

        Only CSS class names are currently supported. Parts of the style string
        that do not begin with ``class:`` will be ignored.

        Args:
            s (str): The input string.

        Returns:
            str: The generated HTML.
        """
        fragments = self._highlight(s)
        tags = ['<span class="highlight">']
        template = '<span class="{}">{}</span>'
        for style, text in fragments:
            classes = []
            if self._pygments_styles:
                classes.append(self._pygments_css_class(style))
            else:
                for st in style.split():
                    if st.startswith('class:'):
                        classes.append(html.escape(st[6:]))
            if classes and classes[0]:
                tags.append(template.format(' '.join(classes), html.escape(text)))
            else:
                tags.append(html.escape(text))
        tags.append('</span>')
        return ''.join(tags)

    def lex_document(self, document):
        lines = list(split_lines(self.highlight(document.text)))
        return lambda i: lines[i]
