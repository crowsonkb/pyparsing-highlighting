"""Syntax highlighting for prompt_toolkit and HTML with pyparsing."""

from .pp_highlighter import DummyStyler, PPHighlighter, Styler
from .pp_validator import PPValidator

dummy_styler = DummyStyler()
"""DummyStyler: An importable instance of :class:`DummyStyler` to pass to parser
factories.
"""

__all__ = ['dummy_styler', 'DummyStyler', 'PPHighlighter', 'PPValidator',
           'Styler']

__version__ = '0.2.8'
