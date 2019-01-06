"""Four-function calculator example."""

from operator import add, sub, mul, truediv

from prompt_toolkit.styles import Style
import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from .repl import repl


def lassoc_mapreduce(func):
    """Parses left-associative binary operators without left recursion."""
    def reducer(t):
        accum = t[0]
        for i in range(2, len(t), 2):
            accum = func(t[i-1])(accum, t[i])
        return accum
    return reducer


def parser_factory(styler=None):
    """Builds the calculator parser.

    If `styler` is specified, parse expressions to be syntax highlighted will
    be assigned classes.
    """
    if styler is None:
        styler = lambda *args: args[1]

    LPAR, RPAR = map(pp.Suppress, '()')
    plus, minus, star, slash = map(lambda s: styler('class:op', pp.Literal(s)), '+-*/')

    value = styler('class:value', ppc.fnumber)

    expr = pp.Forward()

    atom = value | LPAR + expr + RPAR

    neg = minus + atom
    neg.addParseAction(lambda t: -t[1])
    signed_atom = atom | neg

    term = signed_atom + pp.ZeroOrMore((star | slash) + signed_atom)
    term.addParseAction(lassoc_mapreduce(lambda op: {'*': mul, '/': truediv}[op]))

    expr <<= term + pp.ZeroOrMore((plus | minus) + term)
    expr.addParseAction(lassoc_mapreduce(lambda op: {'+': add, '-': sub}[op]))
    expr.setName('expr')

    return expr


def main():
    """The main function."""
    parser = parser_factory()
    style = Style([('op', '#b625b4 bold'), ('value', '#b27a01')])
    repl(parser, parser_factory, style=style)


if __name__ == '__main__':
    main()
