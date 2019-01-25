"""A read-eval-print loop for pyparsing-highlighting examples."""

import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.patch_stdout import patch_stdout
from pyparsing import ParseBaseException

from pp_highlighting import dummy_styler, PPHighlighter, PPValidator


# pylint: disable=too-many-locals
def repl(parser_factory, *, prompt='> ', multiline=False, style=None,
         validate_while_typing=True, validate=True, prompt_continuation=': ',
         uses_pygments_tokens=False):
    """A read-eval-print loop for pyparsing-highlighting examples."""

    def prompt_continuation_fn(*args, **kwargs):
        return prompt_continuation

    parser = parser_factory(dummy_styler)
    pph = PPHighlighter(parser_factory,
                        uses_pygments_tokens=uses_pygments_tokens)
    ppv = PPValidator(parser, multiline=multiline) if validate else None
    history = InMemoryHistory()

    session = PromptSession(prompt, multiline=multiline, lexer=pph,
                            validate_while_typing=validate_while_typing,
                            validator=ppv, style=style, history=history,
                            prompt_continuation=prompt_continuation_fn)

    while True:
        try:
            with patch_stdout():
                s = session.prompt()
            result = parser.parseString(s, parseAll=True)
            for item in result:
                print(repr(item))
        except ParseBaseException as err:
            print('{}: {}'.format(type(err).__name__, err), file=sys.stderr)
        except KeyboardInterrupt:
            pass
        except EOFError:
            break
