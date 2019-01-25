"""A prompt_toolkit Validator for pyparsing."""

from prompt_toolkit.validation import Validator, ValidationError
import pyparsing as pp

__all__ = ['PPValidator']


class PPValidator(Validator):
    """A prompt_toolkit :class:`Validator` for pyparsing."""
    _fmt_multiline = '(line:{}, col:{}) {}'
    _fmt_oneline = '(col:{}) {}'

    def __init__(self, expr, *, multiline=True, move_cursor_to_end=False):
        """Constructs a new :class:`PPValidator`.

        Args:
            expr (pyparsing.ParserElement): The parser to use for validation.
            multiline (bool): Whether to include the line number in the error
                message.
            move_cursor_to_end (bool): Whether to move the cursor to the end
                of the input if a non-pyparsing exception was raised during
                parsing.
        """
        self.expr = expr
        self.move_cursor_to_end = move_cursor_to_end
        self.multiline = multiline

    def __repr__(self):
        return '{0.__class__.__name__}({0.expr!r})'.format(self)

    def validate(self, document):
        try:
            self.expr.parseString(document.text, parseAll=True)
        except pp.ParseBaseException as err:
            if self.multiline:
                msg = self._fmt_multiline.format(err.lineno, err.column, err.msg)
            else:
                msg = self._fmt_oneline.format(err.column, err.msg)
            raise ValidationError(err.loc, msg)
        except Exception as err:  # pylint: disable=broad-except
            i = len(document.text) if self.move_cursor_to_end else 0
            raise ValidationError(i, '{}: {}'.format(type(err).__name__, err))
