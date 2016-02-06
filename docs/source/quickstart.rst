.. quickstart:

Getting Started
===============

Adding Style to a DataFrame
---------------------------

The PrettyPandas class takes advantage of the new `Pandas Style API`_ to create
custom tables for your dataframes. If you have a dataframe ``df``, this is how
that might look:

.. _Pandas Style API: http://pandas.pydata.org/pandas-docs/stable/style.html

.. code-block:: python

    from prettypandas import PrettyPandas

    table = PrettyPandas(df)

.. image:: _static/Images/1@2x.png
    :width: 276px

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

The builtin summary methods are:

* :py:meth:`total <prettypandas.PrettyPandas.total>`
* :py:meth:`average <prettypandas.PrettyPandas.average>`
* :py:meth:`median <prettypandas.PrettyPandas.median>`
* :py:meth:`min <prettypandas.PrettyPandas.min>`
* :py:meth:`max <prettypandas.PrettyPandas.max>`

The above functions work nicely on your table, if you wanted to add a grand
total to the bottom of your table the code is simple:

.. code-block:: python

    PrettyPandas(df).total()

.. image:: _static/Images/total@2x.png
    :width: 311px

And if you want to mix and match summaries:

.. code-block:: python

    PrettyPandas(df).total().average()

.. image:: _static/Images/average@2x.png
    :width: 334px

The ``axis`` parameter specifies which ``numpy`` style axis to apply a summary
on --- 0 for columns, 1 for rows, and ``None`` for both.

.. code-block:: python

    PrettyPandas(df).total(axis=1)

.. image:: _static/Images/alt_axis@2x.png
    :width: 349px

You can even mix and match summaries applied to different axis.

Creating a Custom Summary
^^^^^^^^^^^^^^^^^^^^^^^^^

The :py:meth:`summary <prettypandas.PrettyPandas.summary>` method creates a custom summary
from a function which takes an array-like structure as a list.

.. code-block:: python

    def count_greater_than_five(items):
        return sum(item > 5 for item in items)

    PrettyPandas(df).summary(count_greater_than_five, title="> 5")

.. image:: _static/Images/custom_fn@2x.png
    :width: 287px


Formatting Numbers
------------------

Most reports use at least some units of measurement. PrettyPandas currently
supports percentages, money, and a more general unit method.

* :py:meth:`as_percent <prettypandas.PrettyPandas.as_percent>`
* :py:meth:`as_currency <prettypandas.PrettyPandas.as_currency>`
* :py:meth:`as_unit <prettypandas.PrettyPandas.as_unit>`

The ``as_unit`` method takes a positional ``unit`` argument which indicates the
string representing the unit to be used and a ``location`` argument to specify
whether the unit should be a prefix or suffix to the value.

The ``as_currency`` and ``as_percent`` methods are localized to use whatever
units your Python distribution thinks are best for you. If you aren't getting
the correct units use the :py:meth:`set_locale
<prettypandas.PrettyPandas.set_locale>` method to specify your locale.

If you need to use a different currency, just pass it to ``currency='...'`` to
change it.

The ``as_money`` method takes optional ``currency`` and ``location`` arguments
which work just like the ``as_unit`` method. By default the currency is in
dollars.

.. note::
    Python 2 doesn't support unicode literals by default. You can use `unicode
    literals`_ (e.g. ``u'€'``) or import the unicode literal behaviour from
    Python 3:

    .. code-block:: python

        from __future__ import unicode_literals


.. _unicode literals: https://docs.python.org/2/howto/unicode.html#unicode-literals-in-python-source-code


Formatting Columns
^^^^^^^^^^^^^^^^^^

By default the formatting methods apply to the entire dataframe. When you need
to format just a few columns you can use the ``subset`` argument to specify a
single column, or multiple columns.

.. code-block:: python

    PrettyPandas(df).as_percent(subset='A')  # Format just column A

.. image:: _static/Images/format_a@2x.png
    :width: 301px

.. code-block:: python

    PrettyPandas(df).as_percent(subset=['A', 'B'])  # Format columns A and B

.. image:: _static/Images/format_a_b@2x.png
    :width: 363px

Formatting Rows and Complex Formatting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Formatting rows is more complicated than formatting columns. The `subset`
argument needs to take in a ``pandas.IndexSlice`` to specify the row.

.. code-block:: python

    # Format the row with row-index 3
    PrettyPandas(df, precision=2).as_percent(subset=pd.IndexSlice[3,:])

.. image:: _static/Images/format_row@2x.png
    :width: 294px

For multi-index dataframes subsetting is more complicated. You will need to use
multiple ``pandas.IndexSlice`` objects to get the correct rows.

The following example shows how to select rows in a multi-index:

.. code-block:: python

    idx = pd.IndexSlice
    first_row_idx = idx[:, 1]   # select all with index like (*, 1)
    second_row_idx = idx[:, 2]  # select all with index like (*, 2)

    (PrettyPandas(df2)
     .as_money(subset=idx[first_row_idx, :])
     .as_percent(subset=idx[second_row_idx, :])
     )

.. image:: _static/Images/format_complex@2x.png
    :width: 315px

For more info on Pandas indexing, read `Pandas Indexing`_ and `Pandas Advanced
Indexing`_.

.. _Pandas Indexing: http://pandas.pydata.org/pandas-docs/stable/indexing.html
.. _Pandas Advanced Indexing:
    http://pandas.pydata.org/pandas-docs/stable/advanced.html

Hiding Rows and Columns
-----------------------

When you need to include data in summaries but don't want it displayed,
the :py:meth:`hide <prettypandas.PrettyPandas.hide>` will include data in
summaries, but exclude it from display. It will hide the pandas subset on the
axis specified.


The Magic Function
------------------

The :py:func:`apply_pretty_globals` function will patch your notebook so that
all tables are styled the same. This injects HTML into the notebook (which
some hosts don't allow).
