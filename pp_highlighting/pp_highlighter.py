"""Syntax highlighting with pyparsing."""

from prompt_toolkit.formatted_text import FormattedText, PygmentsTokens, split_lines
from prompt_toolkit.lexers import Lexer
from pygments.token import STANDARD_TYPES, Token
import pyparsing as pp

__all__ = ['PPHighlighter']


class PPHighlighter(Lexer):
    """Syntax highlighting with pyparsing."""
    def __init__(self, parser_factory, *, pygments_styles=False):
        self._fragments = {}
        self._pygments_styles = pygments_styles
        self._parser = parser_factory(self.parser_wrapper)

    def parser_wrapper(self, style, expr):
        """Wraps a pyparsing parse expression to capture text fragments.

        :meth:`parser_wrapper` wraps the given parse expression in
        :func:`pyparsing.originalTextFor` to capture the original text it
        matched, and returns the modified parse expression. You must add
        parse actions to the modified parse expression with
        :meth:`addParseAction` instead of :meth:`setParseAction`, or it will
        stop capturing text.

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

    def _highlight(self, s):
        default_style = Token.Text if self._pygments_styles else ''

        self._fragments = {}
        try:
            self._parser.parseString(s)
        except pp.ParseBaseException:
            pass

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
            Union[FormattedText, PygmentsTokens]: The resulting list of
            prompt-toolkit text fragments.
        """
        fragments = self._highlight(s)
        if self._pygments_styles:
            return PygmentsTokens(fragments)
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
            if self._pygments_styles:
                classes = [self._pygments_css_class(style)]
            else:
                classes = [st[6:] for st in style.split() if st.startswith('class:')]
            if classes and classes[0]:
                tags.append(template.format(' '.join(classes), text))
            else:
                tags.append(text)
        tags.append('</span>')
        return ''.join(tags)

    def lex_document(self, document):
        lines = list(split_lines(self.highlight(document.text)))
        return lambda i: lines[i]
