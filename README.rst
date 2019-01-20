pyparsing-highlighting
======================

Syntax highlighting with `pyparsing <https://github.com/pyparsing/pyparsing>`_, supporting both HTML output and `prompt_toolkit <https://github.com/prompt-toolkit/python-prompt-toolkit>`_–style terminal output. The ``PPHighlighter`` class can also be used as a lexer for syntax highlighting as you type in ``prompt_toolkit``. It is compatible with existing `Pygments <http://pygments.org>`_ styles.

Read the documentation on `readthedocs <https://pyparsing-highlighting.readthedocs.io/en/stable/>`_.

Requirements
------------

- `Python <https://www.python.org>`_ 3.5+
- `prompt_toolkit <https://github.com/prompt-toolkit/python-prompt-toolkit>`_ 2.0+
- `pygments <http://pygments.org>`_
- `pyparsing <https://github.com/pyparsing/pyparsing>`_

Installation
------------

.. code:: bash

   pip3 install -U pyparsing-highlighting

Or, after cloning the repository on GitHub:

.. code:: bash

   python3 setup.py install

Examples
--------

The following code demonstrates the use of ``PPHighlighter``:

.. code:: python

   from pp_highlighting import PPHighlighter
   from prompt_toolkit.styles import Style
   import pyparsing as pp
   from pyparsing import pyparsing_common as ppc

   def parser_factory(styler):
       a = styler('class:int', ppc.integer)
       return pp.delimitedList(a)

   pph = PPHighlighter(parser_factory)
   style = Style([('int', '#528f50')])
   pph.print('1, 2, 3', style=style)

This prints out the following to the terminal:

.. raw:: html

   <img src="docs/source/example_ints.png" width="56px" height="18px">

The following code generates HTML:

.. code:: python

   pph.highlight_html('1, 2, 3')

The output is:

.. code:: HTML

   <span class="highlight"><span class="int">1</span>, <span class="int">2</span>, <span class="int">3</span></span>

There is also a lower-level API: :code:`pph.highlight('1, 2, 3')` returns the following::

   FormattedText([('class:int', '1'), ('', ', '), ('class:int', '2'), ('', ', '), ('class:int', '3')])

A ``FormattedText`` instance can be passed to ``prompt_toolkit.print_formatted_text()``, along with a ``Style`` mapping the class names to colors, for display on the terminal.

``PPHighlighter`` can also be passed to a ``prompt_toolkit.PromptSession`` as the ``lexer`` argument, which will perform syntax highlighting as you type. For an example of this, see ``examples/calc.py`` and ``examples/repl.py``.
