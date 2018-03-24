.. PrettyPandas documentation master file, created by
   sphinx-quickstart on Tue Jan 19 12:59:36 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PrettyPandas
============

PrettyPandas is an extension to the Pandas DataFrame class that helps you
create report qualitiy tables with a simple API.


.. code-block:: python

   (
       df
       .pipe(PrettyPandas)
       .as_currency('GBP', subset='A')
       .as_percent(subset='B')
       .total()
       .average()
   )

.. image:: _static/Images/API@2x.png
    :width: 400px


Features
--------

- Add summary rows and columns.
- Number formatting for currency, scientific units, and percentages.
- Chaining commands.
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

Contents
--------

.. toctree::
   :maxdepth: 3

   Getting Started <quickstart>
   testing
   API <prettypandas>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

