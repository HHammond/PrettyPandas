.. quickstart:

Getting Started
===============

Adding Style to a DataFrame
---------------------------

The PrettyPandas class takes advantage of the new `Pandas Style API
<http://pandas.pydata.org/pandas-docs/stable/style.html>`_ to create custom
tables for your dataframes. If you have a dataframe ``df``, this is how that
might look:

.. code-block:: python

    from prettypandas import PrettyPandas

    table = PrettyPandas(df)

.. note::
    An instance of PrettyPandas is no longer the original dataframe but
    a presentation of the dataframe. That means you cannot use any of the
    standard transformations from the ``pandas.DataFrame`` class. The
    PrettyPandas instance can't change the original dataframe so there's no
    fear of contaminating your data.

Adding Summaries
----------------

PrettyPandas supports many different summary functions, as well the ability to
apply summaries along rows, columns, or both. Summaries chain together so you
can use multiple summaries without any headaches.

The builtin summary functions are:

* :py:meth:`PrettyPandas.total`
* :py:meth:`PrettyPandas.average`
* :py:meth:`PrettyPandas.median`
* :py:meth:`PrettyPandas.min`
* :py:meth:`PrettyPandas.max`

The above functions work nicely on your table, if you wanted to add a grand
total to the bottom of your table the code is simple:

.. code-block:: python

    PrettyPandas(df).total()

And if you want mix and match summaries:

.. code-block:: python

    PrettyPandas(df).total().average()

The ``axis`` parameter specifies which ``numpy`` style axis to apply a summary
on --- 0 for columns, 1 for rows, and ``None`` for both.

.. code-block:: python

    PrettyPandas(df).total(axis=1)


Creating a Custom Summary
^^^^^^^^^^^^^^^^^^^^^^^^^

:py:meth:`PrettyPandas.summary` creates a custom summary from a function which 
takes an array-like structure as a list.

.. code-block:: python

    def count_greater_than_five(items):
        return sum(item > 5 for item in items)

    PrettyPandas(df).summary(count_greater_than_five, title="> 5")


The Magic Function
------------------

The :py:func:`apply_pretty_globals` function will patch your notebook so that
all tables are styled the same. This injects HTML into the notebook (which
some hosts don't allow).
