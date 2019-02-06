"""An example JSON parser.

Note that escape sequences inside strings will be recognized and highlighted
using a different style than the rest of the string.
"""

from prompt_toolkit.styles import Style
import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from .repl import repl


# pylint: disable=too-many-locals
def parser_factory(styler):
    """Builds the JSON parser."""
    LBRK, RBRK, LBRC, RBRC, COLON, DQUO = map(pp.Suppress, '[]{}:"')
    DQUO = styler('class:string', DQUO)

    control_chars = ''.join(map(chr, range(32))) + '\x7f'
    normal_chars = pp.CharsNotIn(control_chars + '\\"')
    s_quo = pp.Literal('\\"').addParseAction(pp.replaceWith('"'))
    s_sol = pp.Literal('\\/').addParseAction(pp.replaceWith('/'))
    s_rsol = pp.Literal('\\\\').addParseAction(pp.replaceWith('\\'))
    s_back = pp.Literal('\\b').addParseAction(pp.replaceWith('\b'))
    s_form = pp.Literal('\\f').addParseAction(pp.replaceWith('\f'))
    s_nl = pp.Literal('\\n').addParseAction(pp.replaceWith('\n'))
    s_ret = pp.Literal('\\r').addParseAction(pp.replaceWith('\r'))
    s_tab = pp.Literal('\\t').addParseAction(pp.replaceWith('\t'))
    s_unicode = pp.Suppress('\\u') + pp.Word(pp.hexnums, exact=4)
    s_unicode.addParseAction(lambda t: chr(int(t[0], 16)))
    escape_seqs = s_quo | s_sol | s_rsol | s_back | s_form | s_nl | s_ret | s_tab | s_unicode
    chars = styler('class:string', normal_chars) | styler('class:escape', escape_seqs)

    skip_white = pp.Optional(pp.Suppress(pp.White()))
    string = skip_white + DQUO - pp.Combine(pp.ZeroOrMore(chars)) + DQUO
    string.leaveWhitespace()
    string.setName('string')

    value = pp.Forward()

    pair = string + COLON + value
    pair.addParseAction(tuple)
    obj = LBRC - pp.Optional(pp.delimitedList(pair)) + pp.NotAny(',') + RBRC
    obj.addParseAction(lambda t: {k: v for k, v in t})
    obj.setName('object')

    array = LBRK - pp.Optional(pp.delimitedList(value)) + pp.NotAny(',') + RBRK
    array.addParseAction(lambda t: [list(t)])
    array.setName('array')

    true = pp.Literal('true').addParseAction(pp.replaceWith(True))
    false = pp.Literal('false').addParseAction(pp.replaceWith(False))
    null = pp.Literal('null').addParseAction(pp.replaceWith(None))
    constant = styler('class:constant', true | false | null)

    value <<= obj | array | string | styler('class:number', ppc.number) | constant
    value.parseWithTabs()
    value.setName('JSON value')
    return value


def main():
    """The main function."""
    print(__doc__)
    style = Style([
        ('constant', '#b27a01 bold'),
        ('escape', '#0092c7'),
        ('number', '#b27a01'),
        ('string', '#528f50'),
    ])
    repl(parser_factory, style=style)


if __name__ == '__main__':
    main()
