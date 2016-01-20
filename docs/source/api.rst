.. api:

API
===

.. _prettypandas-api:

PrettyPandas
------------

.. py:class:: PrettyPandas

    :param data: 
        The dataframe to be used
    :param precision: 
        Decimal precision for values
    :param table_styles: 
        list-like, default None.
    :param uuid: a unique identifier to avoid CSS collisons; 
        generated automatically
    :param caption:
        caption to attach to the table
    :param summary_rows:
        list of single-row dataframes to be appended as a summary
    :param summary_cols:
        list of single-row dataframes to be appended as a summary

    .. py:attribute:: HEADER_PROPERTIES

        List of (property, value) pairs for CSS for header cells.

    .. py:attribute:: SUMMARY_PROPERTIES

        List of (property, value) pairs for CSS for summary cells. Defaults to
        the same as ``HEADER_PROPERTIES``.

    .. py:attribute:: STYLES

        List of ``{'selector': <selector>, 'props': <property list>}``
        dictionaries used to represent the styles of the entire table.
 
    .. py:method:: summary(func, title, axis, **kwargs)

        Add custom summary row or column to table.

        :param func: Function taking array and generating final summary value
        :param title: Title to be used in summary header
        :param axis: Axis to compute summary on; ``None`` for both.
        :param kwargs: keyword arguments to ``func``

    .. py:method:: multi_summary(funcs, titles, axis, **kwargs)

        Simultaneously add multiple custom summary functions to the table.

        :param funcs: List of functions to be used to generate summaries.
        :param titles: List of titles to go with each function.
        :param axis: axis to compute summaries on; ``None`` for both.
        :param kwargs: keyword arguments passed to every function.

    .. py:method:: total(title, axis, **kwargs)

        Add a total row or column to the table.

        :param title: Summary title.
        :param axis: Axis to compute summary on; ``None`` for both.
        :param kwargs: keyword arguments passed to ````numpy.sum```` 


    .. py:method:: average(title, axis, **kwargs)

        Add an average row or column to the table.

        :param title: Summary title.
        :param axis: Axis to compute summary on; ``None`` for both.
        :param kwargs: keyword arguments passed to ``numpy.mean`` 

    .. py:method:: median(title, axis, **kwargs)

        Add a median value row or column to the table.

        :param title: Summary title.
        :param axis: Axis to compute summary on; ``None`` for both.
        :param kwargs: keyword arguments passed to ``numpy.median`` 

    .. py:method:: max(title, axis, **kwargs)

        Add a maximum value row or column to the table.

        :param title: Summary title.
        :param axis: Axis to compute summary on; ``None`` for both.
        :param kwargs: keyword arguments passed to ``numpy.max`` 

    .. py:method:: min(title, axis, **kwargs)

        Add a minimum value row or column to the table.

        :param title: Summary title.
        :param axis: Axis to compute summary on; ``None`` for both.
        :param kwargs: keyword arguments passed to ``numpy.min`` 

    .. py:method:: as_percent(precision=None, subset=None)

        Represent subset of dataframe as percentages.

        :param precision: Integer of decimal precision to be used.
        :param subset: Pandas subset to be represented.

    .. py:method:: as_unit(unit, precision=None, subset=None, \
                               location='prefix')

        Represent subset of dataframe as a special unit.

        :param unit: String representing the unit to be used
        :param location: "prefix" or "suffix" indicating where the unit goes.
        :param precision: Number of decimal places to round to
        :param subset: Pandas subset to be represented.

    .. py:method:: as_money(precision=None, subset=None, currency='$', \
                             location='prefix')

        Represent subset of dataframe as currency

        :param currency: Currency string to be used.
        :param location: "prefix" or "suffix" indicating where the unit goes.
        :param precision: Number of decimal places to round to
        :param subset: Pandas subset to be represented.


The Magic Function
------------------

.. py:function:: apply_pretty_globals()

    Apply global CSS to make dataframes pretty.

    This function injects HTML and CSS code into the notebook in order to make 
    tables look pretty. Third party hosts of notebooks advise against using 
    this and some don't support it. As long as you are okay with HTML injection
    in your notebook, go ahead and use this. Otherwise use the ``PrettyPandas``
    class.
