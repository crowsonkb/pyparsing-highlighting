"""An example S-expression parser."""

from prompt_toolkit.styles import Style
import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from pp_highlighting import dummy_styler
from .repl import repl


class Node:
    """Base class for special S-expression types."""
    def __init__(self, item):
        self.item = item

    def __repr__(self):
        return '{0.__class__.__name__}({0.item!r})'.format(self)


class Symbol(Node):
    """Represents function and variable names."""


class Quote(Node):
    """Represents a quoted form."""


# pylint: disable=too-many-locals
def parser_factory(styler=dummy_styler):
    """Builds the S-expression parser."""
    def cond_optional(expr):
        return pp.Optional(expr) if styler else expr

    LPAR, RPAR, SQUO, DQUO = map(pp.Suppress, '()\'"')

    form_first = pp.Forward()
    form = pp.Forward()

    nil = pp.CaselessKeyword('nil').addParseAction(pp.replaceWith([]))
    t = pp.CaselessKeyword('t').addParseAction(pp.replaceWith(True))
    constant = styler('class:constant', nil | t)

    number = styler('class:number', ppc.number).setName('number')

    control_chars = ''.join(map(chr, range(0, 32))) + '\x7f'
    symbol = pp.CharsNotIn(control_chars + '\'"`;,()[]{} ')
    symbol = styler('class:symbol', symbol).setName('symbol')
    symbol.addParseAction(lambda toks: Symbol(toks[0]))
    call = styler('class:call', symbol)

    string = DQUO + pp.Combine(pp.Optional(pp.CharsNotIn('"'))) + cond_optional(DQUO)
    string = styler('class:string', string).setName('string')

    forms = (form_first + pp.ZeroOrMore(form)).setName('one or more forms')
    sexp = (LPAR + pp.Optional(forms) + cond_optional(RPAR)).setName('s-expression')
    sexp.addParseAction(lambda toks: [list(toks)])

    quote = (styler('class:quote', SQUO) + form).setName('quoted form')
    quote.addParseAction(lambda toks: Quote(toks[0]))

    form_first <<= constant | number ^ call | string | sexp | quote
    form <<= constant | number ^ symbol | string | sexp | quote

    return form


def main():
    """The main function."""
    parser = parser_factory()
    style = Style.from_dict({
        'call': '#4078f2',
        'constant': '#b27a01 bold',
        'number': '#b27a01',
        'quote': '#0092c7',
        'string': '#528f50',
    })
    repl(parser, parser_factory, style=style)


if __name__ == '__main__':
    main()
