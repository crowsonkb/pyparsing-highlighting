pyparsing-highlighting
======================

Syntax highlighting with `pyparsing <https://github.com/pyparsing/pyparsing>`_, supporting both HTML output and `prompt_toolkit <https://github.com/prompt-toolkit/python-prompt-toolkit>`_–style terminal output. The ``PPHighlighter`` class can also be used as a lexer for syntax highlighting as you type in prompt_toolkit. It is compatible with existing `Pygments <http://pygments.org>`_ styles.

The main benefit of pyparsing-highlighting over Pygments is that pyparsing parse expressions are both more powerful and easier to understand than Pygments lexers. pyparsing implements `parsing expression grammars <https://en.wikipedia.org/wiki/Parsing_expression_grammar>`_ using `parser combinators <https://en.wikipedia.org/wiki/Parser_combinator>`_, which means that higher level parse expressions are built up in Python code out of lower level parse expressions in a straightforward to construct, readable, modular, well-structured, and easily maintainable way.

See `the official pyparsing documentation <https://pyparsing-docs.readthedocs.io/en/latest/index.html>`_ or `my unofficial (epydoc) documentation <https://pyparsing-doc.neocities.org>`_; read the pyparsing-highlighting documentation on `readthedocs <https://pyparsing-highlighting.readthedocs.io/en/latest/>`_.

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

Or, after cloning the repository on GitHub:

.. code:: bash

   python3 setup.py install

(or, with PyPy):

.. code:: bash

   pypy3 setup.py install

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

.. image:: https://raw.githubusercontent.com/crowsonkb/pyparsing-highlighting/master/docs/source/example_ints.png
   :width: 56
   :height: 18
   :alt: 1, 2, 3

The following code generates HTML:

.. code:: python

   pph.highlight_html('1, 2, 3')

The output is:

.. code:: HTML

   <pre class="highlight"><span class="int">1</span>, <span class="int">2</span>, <span class="int">3</span></pre>

There is also a lower-level API—:code:`pph.highlight('1, 2, 3')` returns the following::

   FormattedText([('class:int', '1'), ('', ', '), ('class:int', '2'), ('', ', '), ('class:int', '3')])

A ``FormattedText`` instance can be passed to ``prompt_toolkit.print_formatted_text()``, along with a ``Style`` mapping the class names to colors, for display on the terminal. See the prompt_toolkit `formatted text documentation <https://python-prompt-toolkit.readthedocs.io/en/stable/pages/printing_text.html#style-text-tuples>`_ and `formatted text API documentation <https://python-prompt-toolkit.readthedocs.io/en/stable/pages/reference.html#module-prompt_toolkit.formatted_text>`_.

``PPHighlighter`` can also be passed to a ``prompt_toolkit.PromptSession`` as the ``lexer`` argument, which will perform syntax highlighting as you type. For examples of this, see ``examples/calc.py``, ``examples/json_pph.py``, ``examples/repr.py``, and ``examples/sexp.py``. The examples can be run by (from the project root directory):

.. code:: bash

   python3 -m examples.calc
   python3 -m examples.json_pph
   python3 -m examples.repr
   python3 -m examples.sexp
