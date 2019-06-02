Welcome to pyparsing-highlighting's documentation!
==================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

- `View on GitHub <https://github.com/crowsonkb/pyparsing-highlighting>`_

Syntax highlighting with `pyparsing <https://github.com/pyparsing/pyparsing>`_, supporting both HTML output and `prompt_toolkit <https://github.com/prompt-toolkit/python-prompt-toolkit>`_–style terminal output. The :class:`PPHighlighter` class can also be used as a lexer for syntax highlighting as you type in prompt_toolkit. It is compatible with existing `Pygments <http://pygments.org>`_ styles.

The main benefit of pyparsing-highlighting over Pygments is that pyparsing parse expressions are both more powerful and easier to understand than Pygments lexers. pyparsing implements `parsing expression grammars <https://en.wikipedia.org/wiki/Parsing_expression_grammar>`_ using `parser combinators <https://en.wikipedia.org/wiki/Parser_combinator>`_, which means that higher level parse expressions are built up in Python code out of lower level parse expressions in a straightforward to construct, readable, modular, well-structured, and easily maintainable way.

See `the official pyparsing documentation <https://pyparsing-docs.readthedocs.io/en/latest/index.html>`_ or `my unofficial (epydoc) documentation <https://pyparsing-doc.neocities.org>`_.

Requirements
------------

- `Python <https://www.python.org>`_ 3.5+

Note that `PyPy <https://pypy.org>`_, a JIT compiler implementation of Python, is often able to achieve around 5x the performance of CPython, the reference Python implementation.

- `pyparsing <https://github.com/pyparsing/pyparsing>`_
- `prompt_toolkit <https://github.com/prompt-toolkit/python-prompt-toolkit>`_ 2.0+
- `Pygments <http://pygments.org>`_ (optional; needed to use Pygments styles)

Installation
------------

.. code:: bash

   pip3 install -U pyparsing-highlighting

Or, after cloning the repository `on GitHub <https://github.com/crowsonkb/pyparsing-highlighting>`_:

.. code:: bash

   python3 setup.py install

(or, with PyPy):

.. code:: bash

   pypy3 setup.py install

Examples
--------

The following code demonstrates the use of :class:`PPHighlighter`:

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

.. image:: example_ints.png
   :scale: 50%

The following code generates HTML:

.. code:: python

   pph.highlight_html('1, 2, 3')

The output is:

.. code:: HTML

   <pre class="highlight"><span class="int">1</span>, <span class="int">2</span>, <span class="int">3</span></pre>

There is also a lower-level API—:code:`pph.highlight('1, 2, 3')` returns the following::

   FormattedText([('class:int', '1'), ('', ', '), ('class:int', '2'), ('', ', '), ('class:int', '3')])

A :class:`FormattedText` instance can be passed to :func:`prompt_toolkit.print_formatted_text`, along with a :class:`Style` mapping the class names to colors, for display on the terminal. See the prompt_toolkit `formatted text documentation <https://python-prompt-toolkit.readthedocs.io/en/stable/pages/printing_text.html#style-text-tuples>`_ and `formatted text API documentation <https://python-prompt-toolkit.readthedocs.io/en/stable/pages/reference.html#module-prompt_toolkit.formatted_text>`_.

:class:`PPHighlighter` can also be passed to a :class:`prompt_toolkit.PromptSession` as the `lexer` argument, which will perform syntax highlighting as you type. For examples of this, see ``examples/calc.py``, ``examples/json_pph.py``, ``examples/repr.py``, and ``examples/sexp.py``.  The examples can be run by (from the project root directory):

.. code:: bash

   python3 -m examples.calc
   python3 -m examples.json_pph
   python3 -m examples.repr
   python3 -m examples.sexp

Error Handling
--------------

If the parse expression should fail to match, it will be tried again at successive locations until it succeeds. Text encountered during retrying will be passed through unstyled. For example:

.. code:: python

   from pp_highlighting import PPHighlighter
   import pyparsing as pp
   from pyparsing import pyparsing_common as ppc

   def parser_factory(styler):
       return styler('ansicyan', ppc.integer) + styler('ansired', ppc.identifier)

   pph = PPHighlighter(parser_factory)
   pph.print('1a 2b three 4c')

The output is:

.. image:: 1234.png
   :scale: 50%

Note that *this parse expression does not explicitly match more than one integer/identifier pair*. After it matches, it is retried on the space after the first pair, which fails, and then it is retried again starting on the first character of the second pair, which succeeds. It is then retried until it reaches ``4c``, which succeeds.

It is often possible to take advantage of pyparsing-highlighting's error handling to write a simplified parse expression that does not parse a language fully but which still does 'lexer-like' analysis in a way that is robust to errors, and which continues to work even while the user is still typing. ``examples/repr.py`` is an example along these lines.

Testing
-------

(From the project root directory):

To run the unit tests:

.. code:: bash

   python3 -m unittest

To run the regression benchmark:

.. code:: bash

   python3 -m tests.benchmark

Module pp_highlighting
----------------------

.. automodule:: pp_highlighting
   :members:
   :show-inheritance:
   :special-members: __init__, __call__

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
