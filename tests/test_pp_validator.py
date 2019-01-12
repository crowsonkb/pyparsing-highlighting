"""Unit tests for pp_validator."""

# pylint: disable=missing-docstring

import unittest

from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError
import pyparsing as pp

from pp_highlighting import PPValidator

def exception():
    raise RuntimeError('test')

parser = pp.OneOrMore(pp.Literal('test'))
parser_exception = parser.copy().addParseAction(exception)


class TestPPValidator(unittest.TestCase):
    def test_succeed(self):  # pylint: disable=no-self-use
        ppv = PPValidator(parser)
        ppv.validate(Document('test'))

    def test_fail(self):
        ppv = PPValidator(parser)
        with self.assertRaises(ValidationError):
            ppv.validate(Document('fail'))

    def test_cursor_position(self):
        ppv = PPValidator(parser)
        try:
            ppv.validate(Document('test fail'))
        except ValidationError as err:
            self.assertEqual(err.cursor_position, 5)
        else:
            self.fail()

    def test_message(self):
        ppv = PPValidator(parser, multiline=False)
        try:
            ppv.validate(Document('test fail'))
        except ValidationError as err:
            self.assertRegex(err.message, r'\(col:6\) .*')
        else:
            self.fail()

    def test_message_multiline(self):
        ppv = PPValidator(parser)
        try:
            ppv.validate(Document('test\ntest fail'))
        except ValidationError as err:
            self.assertRegex(err.message, r'\(line:2, col:6\) .*')
        else:
            self.fail()

    def test_exception(self):
        ppv = PPValidator(parser_exception)
        try:
            ppv.validate(Document('test'))
        except ValidationError as err:
            self.assertEqual(err.cursor_position, 0)
            self.assertEqual(err.message, 'RuntimeError: test')
        else:
            self.fail()

    def test_exception_move_cursor_to_end(self):
        ppv = PPValidator(parser_exception, move_cursor_to_end=True)
        try:
            ppv.validate(Document('test'))
        except ValidationError as err:
            self.assertEqual(err.cursor_position, 4)
            self.assertEqual(err.message, 'RuntimeError: test')
        else:
            self.fail()


if __name__ == '__main__':
    unittest.main()
