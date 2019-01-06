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
        self._parser = parser_factory(self._make_fragment_action)

    def _make_fragment_action(self, style, parser=None):
        def action(s, loc, toks):
            self._fragments[loc] = (style, s[loc:loc + len(toks[0])])
        if parser is None:
            return action
        new_parser = parser.copy()
        new_parser.setParseAction(action)
        return new_parser

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
            css_class = STANDARD_TYPES[token]
        except KeyError:
            css_class = cls._pygments_css_class(token.parent)
        return css_class

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
