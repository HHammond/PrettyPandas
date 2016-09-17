from __future__ import unicode_literals

from IPython.display import HTML
import numpy as np
import pandas as pd
from pandas.core.indexing import _non_reducing_slice

from collections import namedtuple
from itertools import chain
from functools import partial
import warnings

from .formatters import as_percent, as_money, as_unit, as_currency, LOCALE_OBJ

if pd.__version__ >= '0.18.1':
    from pandas.formats.style import Styler
else:
    from pandas.core.style import Styler


def _parse_axis(axis):
    if axis == 'index':
        return 0
    if axis == 'columns':
        return 1
    return axis


def apply_pretty_globals():
    """Apply global CSS to make dataframes pretty.

    This function injects HTML and CSS code into the notebook in order to make
    tables look pretty. Third party hosts of notebooks advise against using
    this and some don't support it. As long as you are okay with HTML injection
    in your notebook, go ahead and use this. Otherwise use the ``PrettyPandas``
    class.
    """

    return HTML("""
        <style type='text/css'>
            /* Pretty Pandas Dataframes */
            .dataframe * {border-color: #c0c0c0 !important;}
            .dataframe th{background: #eee;}
            .dataframe td{
                background: #fff;
                text-align: right;
                min-width:5em;
            }

            /* Format summary rows */
            .dataframe-summary-row tr:last-child,
            .dataframe-summary-col td:last-child{
                background: #eee;
                font-weight: 500;
            }
        </style>
        """)


Formatter = namedtuple("Formatter", "subset, function")
Summarizer = namedtuple("Summarizer", "func, title, axis, subset, kwargs")


class PrettyPandas(Styler):
    """Pretty pandas dataframe Styles.

    Parameters
    ----------
    :param data: Series or DataFrame
    :param precision: int
        precision to round floats to, defaults to pd.options.display.precision
    :param table_styles: list-like, default None
        list of {selector: (attr, value)} dicts. These values overwrite the
        default style.
    :param uuid: str, default None
        a unique identifier to avoid CSS collisons; generated automatically
    :param caption: str, default None
        caption to attach to the table
    :param summary_rows:
        list of single-row dataframes to be appended as a summary
    :param summary_cols:
        list of single-row dataframes to be appended as a summary
    """

    #: Default colour for header backgrounds
    DEFAULT_BACKGROUND = "#eee"

    #: Default color for table borders
    DEFAULT_BORDER_COLOUR = '#c0c0c0'

    #: CSS style for header rows and column.
    HEADER_PROPERTIES = [('background', DEFAULT_BACKGROUND),
                         ('font-weight', '500')]

    #: CSS style for summary content cells.
    SUMMARY_PROPERTIES = HEADER_PROPERTIES

    #: Base styles
    STYLES = [
        {'selector': 'th', 'props': HEADER_PROPERTIES},
        {'selector': 'td', 'props': [('text-align', 'right'),
                                     ('min-width', '3em')]},
        {'selector': '*', 'props': [('border-color', DEFAULT_BORDER_COLOUR)]},
    ]

    #: Default local for formatting functions
    DEFAULT_LOCALE = LOCALE_OBJ

    def __init__(self,
                 data,
                 summary_rows=None,
                 summary_cols=None,
                 formatters=None,
                 *args,
                 **kwargs):

        kwargs['table_styles'] = self.STYLES + kwargs.get('table_styles', [])

        self.summary_rows = summary_rows or []
        self.summary_cols = summary_cols or []
        self.formatters = formatters or []

        return super(self.__class__, self).__init__(data, *args, **kwargs)

    @classmethod
    def set_locale(cls, locale):
        """Set the PrettyPandas default locale."""
        cls.DEFAULT_LOCALE = locale

    def _append_selector(self, selector, *props):
        """Add a CSS selector and style to this Styler."""
        self.table_styles.append({'selector': selector, 'props': props})

    def summary(self, func=np.sum, title='Total', axis=0, subset=None,
                **kwargs):
        """Add multiple summary rows or columns to the dataframe.

        Parameters
        ----------
        :param func: Iterable of functions to be used for a summary.
        :param titles: Iterable of titles in the same order as the functions.
        :param axis:
            Same as numpy and pandas axis argument. A value of None will cause
            the summary to be applied to both rows and columns.
        :param kwargs: Keyword arguments passed to all the functions.

        The results of summary can be chained together.
        """

        axis = _parse_axis(axis)

        if axis == 0:
            subset = subset or self.data.columns
        elif axis == 1:
            subset = subset or self.data.index.values

        summarizer = Summarizer(func, title, axis, subset, kwargs)

        if axis == 0 or axis is None:
            self.summary_rows.append(summarizer)
        if axis == 1 or axis is None:
            self.summary_cols.append(summarizer)

        return self

    def total(self, title="Total", **kwargs):
        """Add a total summary to this table.

        :param title: Title to be displayed.
        :param kwargs: Keyword arguments passed to ``numpy.sum``.
        """
        return self.summary(np.sum, title, **kwargs)

    def average(self, title="Average", **kwargs):
        """Add a mean summary to this table.

        :param title: Title to be displayed.
        :param kwargs: Keyword arguments passed to ``numpy.mean``.
        """
        return self.summary(np.mean, title, **kwargs)

    def median(self, title="Median", **kwargs):
        """Add a median summary to this table.

        :param title: Title to be displayed.
        :param kwargs: Keyword arguments passed to ``numpy.median``.
        """
        return self.summary(np.median, title, **kwargs)

    def max(self, title="Maximum", **kwargs):
        """Add a maximum summary to this table.

        :param title: Title to be displayed.
        :param kwargs: Keyword arguments passed to ``numpy.max``.
        """
        return self.summary(np.max, title, **kwargs)

    def min(self, title="Minimum", **kwargs):
        """Add a minimum summary to this table.

        :param title: Title to be displayed.
        :param kwargs: Keyword arguments passed to ``numpy.min``.
        """
        return self.summary(np.min, title, **kwargs)

    def as_percent(self, subset=None, precision=None, locale=None):
        """Represent subset of dataframe as percentages.

        Parameters:
        -----------
        :param subset: Pandas slice to convert to percentages
        :param precision: int
            Number of decimal places to round to
        :param locale: Locale to be used (e.g. 'en_US')
        """
        add_formatter = partial(self._format_cells,
                                as_percent,
                                subset=subset)
        if locale is not None:
            return add_formatter(locale=locale)
        else:
            return add_formatter(locale=self.DEFAULT_LOCALE)

    def as_currency(self, subset=None, currency='USD', locale=None):
        """Represent subset of dataframe as currency.

        Parameters:
        -----------
        :param subset: Pandas slice to convert to percentages
        :param currency: Currency or currency symbol to be used
        :param locale: Locale to be used (e.g. 'en_US')
        """
        add_formatter = partial(self._format_cells,
                                as_currency,
                                subset=subset,
                                currency=currency)

        if locale is not None:
            return add_formatter(locale=locale)
        else:
            return add_formatter(locale=self.DEFAULT_LOCALE)

    def as_unit(self, unit, subset=None, precision=None, location='prefix'):
        """Represent subset of dataframe as a special unit.

        Parameters:
        -----------
        :param unit: string representing unit to be used.
        :param subset: Pandas slice to convert to percentages
        :param precision: int
            Number of decimal places to round to
        :param location: 'prefix' or 'suffix' indicating where the currency
            symbol should be.
        """
        precision = self.precision if precision is None else precision

        return self._format_cells(as_unit,
                                  subset=subset,
                                  precision=precision,
                                  unit=unit,
                                  location=location)

    def as_money(self,
                 subset=None,
                 precision=None,
                 currency='$',
                 location='prefix'):
        """[DEPRECATED] Represent subset of dataframe as currency.

        Parameters:
        -----------
        :param precision: int
            Number of decimal places to round to
        :param subset: Pandas slice to convert to percentages
        :param currency: Currency string
        :param location: 'prefix' or 'suffix' indicating where the currency
            symbol should be.
        """
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            warnings.warn("`as_money` is depricated in favour of "
                          "`as_currency`.",
                          DeprecationWarning)

        precision = self.precision if precision is None else precision

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return self._format_cells(as_money,
                                      currency=currency,
                                      precision=precision,
                                      subset=subset,
                                      location=location)

    def _format_cells(self, func, subset=None, **kwargs):
        """Add formatting function to cells."""

        self.formatters.append(Formatter(subset=subset,
                                         function=partial(func)))
        return self

    def _apply_formatters(self):
        """Apply all added formatting."""

        def format_if_possible(value, fn):
            try:
                return fn(value)
            except:
                return str(value)

        for subset, function in self.formatters:
            if subset is None:
                subset = self.data.index
            else:
                subset = _non_reducing_slice(subset)

            slice = self.data.ix[subset].applymap(
                partial(format_if_possible, fn=function)
            )
            self.data.ix[subset] = slice
        return self

    def _apply_summaries(self):
        """Add all summary rows and columns."""
        rows = []
        cols = []
        rownames = []
        colnames = []
        summaries = chain(self.summary_rows, self.summary_cols)
        for func, title, axis, subset, kwargs in summaries:
            data = self.data if axis == 0 else self.data.T

            row = data[subset].apply(func, **kwargs)
            row.name = title
            row = row.to_frame().T

            if axis == 0:
                rows.append(row)
                rownames.append(title)
            else:
                cols.append(row)
                colnames.append(title)

        for row in rows:
            self.data = self.data.append(row)
        for col in cols:
            self.data = self.data.T.append(col).T

        for i, _ in enumerate(rows):
            self._append_selector('tr:nth-last-child({})'.format(i + 1),
                                  *self.SUMMARY_PROPERTIES)
        for i, _ in enumerate(cols):
            self._append_selector('td:nth-last-child({})'.format(i + 1),
                                  *self.SUMMARY_PROPERTIES)

        for r in rownames:
            self.data.ix[r, :] = self.data.ix[r, :].fillna('')
        for c in colnames:
            self.data.ix[:, c] = self.data.ix[:, c].fillna('')

        return self

    def _translate(self):
        """Apply styles and formats before rendering."""
        data = self.data.copy()

        self._apply_summaries()
        self._apply_formatters()
        result = super(self.__class__, self)._translate()

        self.data = data
        return result
