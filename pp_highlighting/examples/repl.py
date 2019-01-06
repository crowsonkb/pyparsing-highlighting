"""A read-eval-print loop for pyparsing-highlighting examples."""

import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.patch_stdout import patch_stdout
from pyparsing import ParseBaseException

from pp_highlighting import PPHighlighter


def repl(expr, hl_factory=None, *, prompt='> ', prompt_continuation=': ',
         multiline=False, style=None, pygments_styles=False):
    """A read-eval-print loop for pyparsing-highlighting examples."""

    def prompt_continuation_fn(width, line_number, is_soft_wrap):
        return prompt_continuation

    lexer = None
    if hl_factory is not None:
        lexer = PPHighlighter(hl_factory, pygments_styles=pygments_styles)

    session = PromptSession(prompt, multiline=multiline, lexer=lexer,
                            style=style, history=InMemoryHistory(),
                            prompt_continuation=prompt_continuation_fn)

    while True:
        try:
            with patch_stdout():
                s = session.prompt()
            result = expr.parseString(s, parseAll=True)
            for item in result:
                print(repr(item))
        except ParseBaseException as err:
            print('{}: {}'.format(type(err).__name__, err), file=sys.stderr)
        except KeyboardInterrupt:
            pass
        except EOFError:
            break
