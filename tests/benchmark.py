"""A PPHighlighter benchmark."""

# pylint: disable=no-name-in-module

import random
import time

from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import Python3Lexer
import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from pp_highlighting import dummy_styler, PPHighlighter

N_RUNS = 5


def parser_factory(styler):
    """Builds a parser for nested comma-separated lists of integers (like
    [1, 2, [3]]).
    """
    LBRK, RBRK = map(pp.Suppress, '[]')
    lst = pp.Forward()
    integer = styler('class:int', ppc.integer)
    lst <<= LBRK + pp.Optional(pp.delimitedList(integer | lst)) + RBRK
    lst.addParseAction(lambda t: [list(t)])
    lst.validate()
    return lst


def main():
    """The main function."""
    expr = parser_factory(dummy_styler)
    pph = PPHighlighter(parser_factory)
    lexer = Python3Lexer()
    formatter = Terminal256Formatter()

    # Generate the test data
    random.seed(0)
    data = [[random.randrange(1000) for _ in range(100)] for _ in range(100)]
    s = str(data)

    # Perform the benchmarks
    t1 = time.perf_counter()
    for _ in range(N_RUNS):
        result = expr.parseString(s, parseAll=True)[0]
    t2 = time.perf_counter()
    for _ in range(N_RUNS):
        fragments = pph.highlight(s)
    t3 = time.perf_counter()
    for _ in range(N_RUNS):
        highlight(s, lexer, formatter)
    t4 = time.perf_counter()

    # Verify the results
    assert data == result
    assert s == ''.join(text for _, text in fragments)

    # Display the results
    print('Input string size: {} chars'.format(len(s)))
    print('Parsing completed in {:.3f}ms'.format((t2 - t1) / N_RUNS * 1000))
    print('Highlighting completed in {:.3f}ms'.format((t3 - t2) / N_RUNS * 1000))
    print('Pygments highlighting completed in {:.3f}ms'.format((t4 - t3) / N_RUNS * 1000))


if __name__ == '__main__':
    main()
