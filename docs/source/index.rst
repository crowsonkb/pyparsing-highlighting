Welcome to pyparsing-highlighting's documentation!
==================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

- `View on GitHub <https://github.com/crowsonkb/pyparsing-highlighting>`_

Syntax highlighting with `pyparsing <https://github.com/pyparsing/pyparsing>`_, supporting both HTML output and `prompt_toolkit <https://github.com/prompt-toolkit/python-prompt-toolkit>`_–style terminal output. The ``PPHighlighter`` class can also be used as a lexer for syntax highlighting as you type in ``prompt_toolkit``. It is compatible with existing `Pygments <http://pygments.org>`_ styles.

Requirements
------------

- `Python <https://www.python.org>`_ 3.5+
- `prompt_toolkit <https://github.com/prompt-toolkit/python-prompt-toolkit>`_ 2.0+
- `pygments <http://pygments.org>`_
- `pyparsing <https://github.com/pyparsing/pyparsing>`_

Installation
------------

After cloning the repository:

.. code:: bash

   python3 setup.py install

Examples
--------

The following code demonstrates the use of ``PPHighlighter``:

.. code:: python

   from pp_highlighting import PPHighlighter
   import pyparsing as pp
   from pyparsing import pyparsing_common as ppc

   def parser_factory(styler):
       a = styler('class:int', ppc.integer)
       return pp.delimitedList(a)

   pph = PPHighlighter(parser_factory)
   pph.highlight('1, 2, 3')

``pph.highlight('1, 2, 3')`` returns the following::

   FormattedText([('class:int', '1'), ('', ', '), ('class:int', '2'), ('', ', '), ('class:int', '3')])

A ``FormattedText`` instance can be passed to ``prompt_toolkit.print_formatted_text()``, along with a ``Style`` mapping the class names to colors, for display on the terminal. ``PPHighlighter`` also has a ``highlight_html()`` method which returns the generated HTML as a string.

``PPHighlighter`` can also be passed to a ``prompt_toolkit.PromptSession`` as the ``lexer`` argument, which will perform syntax highlighting as you type. For an example of this, see ``pp_highlighting/examples/calc.py`` and ``pp_highlighting/examples/repl.py``.

Module pp_highlighting
----------------------

.. automodule:: pp_highlighting
   :members:
   :special-members: __init__

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
