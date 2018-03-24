PrettyPandas
============

PrettyPandas is an extension to the Pandas DataFrame class that helps you
create report qualitiy tables with a simple API.

Features
--------

- Add summary rows and columns.
- Number formatting for currency, scientific units, and percentages.
- Chaining commands in a Fluent API.
- Works seamlessly with `Pandas Style API`_.

.. note::

   Version 0.0.4 removes the ``apply_pretty_globals`` function and other custom
   CSS properties because Pandas and Jupyter now defaults to providing great
   looking html tables. If you still want custom CSS you can use the `Pandas
   Style API`_.

.. _Pandas Style API: http://pandas.pydata.org/pandas-docs/stable/style.html>

Installation
------------

You can install PrettyPandas using ``pip`` with support for Python 2.7, 3.3,
3.4, and 3.5:

.. code-block:: sh

    pip install prettypandas


You can also install from source:

.. code-block:: sh

    git clone git@github.com:HHammond/PrettyPandas.git
    cd PrettyPandas
    python setup.py install


Contributing
------------

The project is available on `GitHub`_ and anyone is welcome to contribute. You
can use the `issue tracker`_ to report issues, bugs, or suggest improvements.

.. _GitHub: https://github.com/HHammond/PrettyPandas/
.. _issue tracker: https://github.com/HHammond/PrettyPandas/issues


Documentation
-------------

See the `GitHub page <http://github.com/HHammond/PrettyPandas>`_ for
documentation.


License
-------

The MIT License (MIT)

Copyright (c) 2016 Henry Hammond

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
