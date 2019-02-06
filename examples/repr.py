"""A Python repr() syntax highlighter."""

from prompt_toolkit.styles import Style
import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from .repl import repl


# pylint: disable=too-many-locals
def parser_factory(styler):
    """Builds the repr() parser."""
    squo = styler('class:string', "'")
    dquo = styler('class:string', '"')

    esc_single = pp.oneOf(r'\\ \' \" \n \r \t')
    esc_hex = pp.Literal(r'\x') + pp.Word(pp.hexnums, exact=2)
    escs = styler('class:escape', esc_single | esc_hex)

    control_chars = ''.join(map(chr, range(32))) + '\x7f'
    normal_chars_squo = pp.CharsNotIn(control_chars + r"\'")
    chars_squo = styler('class:string', normal_chars_squo) | escs
    normal_chars_dquo = pp.CharsNotIn(control_chars + r'\"')
    chars_dquo = styler('class:string', normal_chars_dquo) | escs

    skip_white = pp.Optional(pp.White())
    bytes_prefix = pp.Optional(styler('class:string_prefix', 'b'))
    string_squo = skip_white + bytes_prefix + squo - pp.ZeroOrMore(chars_squo) + squo
    string_dquo = skip_white + bytes_prefix + dquo - pp.ZeroOrMore(chars_dquo) + dquo
    string = string_squo | string_dquo
    string.leaveWhitespace()

    address = styler('class:address', '0x' + pp.Word(pp.hexnums))
    number = styler('class:number', ppc.number)
    const = pp.oneOf('True False None NotImplemented Ellipsis ...')
    const = styler('class:constant', const)
    kwarg = styler('class:kwarg', ppc.identifier) + styler('class:operator', '=')
    call = styler('class:call', ppc.identifier) + pp.FollowedBy('(')
    magic = styler('class:magic', pp.Regex(r'__[a-zA-Z0-9_]+__'))

    token = string | address | number | const | kwarg | call | magic
    token.parseWithTabs()
    return pp.originalTextFor(token)


def main():
    """The main function."""
    print(__doc__)
    style = Style([
        ('address', '#e45649'),
        ('call', '#4078f2'),
        ('constant', '#b27a01 bold'),
        ('escape', '#0092c7'),
        ('kwarg', '#b27a01 italic'),
        ('magic', '#e45649'),
        ('number', '#b27a01'),
        ('operator', '#b625b4 bold'),
        ('string', '#528f50'),
        ('string_prefix', '#528f50 bold'),
    ])
    repl(parser_factory, style=style, validate=False, prints_result=False,
         prints_exceptions=False)


if __name__ == '__main__':
    main()
