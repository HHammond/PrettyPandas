from __future__ import unicode_literals

from IPython.display import HTML
from pandas.core.style import Styler
from pandas.core.indexing import _non_reducing_slice
import pandas as pd
import numpy as np

from collections import namedtuple
from itertools import product
from functools import partial
from numbers import Number
import warnings

from .formatters import as_percent, as_money, as_unit, as_currency, LOCALE_OBJ


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
remove_nan_formatter = lambda x: '' if x == np.nan else x

def PrettyPandasNoIndex(dataframe, table_styles = [], *args, **kwargs):
    return PrettyPandas(dataframe, 
                        *args, 
                        table_styles = table_styles + [{'selector': '.row_heading', 'props': [('display', 'none')]}, 
                                                       {'selector': '.blank', 'props': [('display', 'none')]}],
                        **kwargs)
                        
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
                 replace_all_nans_with=None,
                 *args,
                 **kwargs):

        kwargs['table_styles'] = self.STYLES + kwargs.get('table_styles', [])

        self.summary_rows = summary_rows or []
        self.summary_cols = summary_cols or []
        self.formatters = formatters or []
        self.replace_all_nans_with = replace_all_nans_with

        return super(self.__class__, self).__init__(data, *args, **kwargs)

    @classmethod
    def set_locale(cls, locale):
        """Set the PrettyPandas default locale."""
        cls.DEFAULT_LOCALE = locale

    def _append_selector(self, selector, *props):
        """Add a CSS selector and style to this Styler."""
        self.table_styles.append({'selector': selector, 'props': props})

    def summary(self, func=np.sum, title='Total', axis=0, **kwargs):
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
        return self.multi_summary([func], [title], axis, **kwargs)

    def multi_summary(self, funcs, titles, axis=0, subset=None, exclude=None, **kwargs):
        """Add multiple summary rows or columns to the dataframe.

        Parameters
        ----------
        :param funcs: Iterable of functions to be used for a summary.
        :param titles: Iterable of titles in the same order as the functions.
        :param axis:
            Same as numpy and pandas axis argument. A value of None will cause
            the summary to be applied to both rows and columns.
        :param kwargs: Keyword arguments passed to all the functions.
        """
        if axis is None:
            return self.multi_summary(funcs, titles, axis=0, **kwargs)\
                       .multi_summary(funcs, titles, axis=1, **kwargs)

        output = []
        if axis == 0:
            df = self.data.transpose() #use df to iterate over the rows of the transpose of self.data (i.e. cols of self.data)
        else:
            df = self.data
            
        if exclude is not None and subset is None:
            subset = [n for n in list(df.index) if n not in exclude]
            
        for f, t in zip(funcs, titles):
            if subset is None:
                output.append(self.data.apply(f, axis=axis, **kwargs).to_frame(t)) #apply returns Series, to_frame converts to DataFrame
            elif subset is not None:
                summary_vals = [f(vals, **kwargs) if item_name in subset else None for item_name, vals in df.iterrows()]
                output.append(pd.DataFrame(data = {t: summary_vals}, index = df.index))  #dataframe with column name t and values summary_vals

        if axis == 0:
            self.summary_rows += [row.T for row in output]
        elif axis == 1:
            self.summary_cols += output
        else:
            ValueError("Invalid axis selected. Can only use 0, 1, or None.")

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
        return self.summary(np.average, title, **kwargs)

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

    def as_percent(self, subset=None, precision=0, **kwargs):
        """Represent subset of dataframe as percentages.

        Parameters:
        -----------
        :param subset: Pandas slice to convert to percentages
        :param precision: int
            Number of decimal places to round to
        """

        return self._format_cells(as_percent,
                                  subset=subset, 
                                  precision=precision,
                                  **kwargs)

    def as_currency(self, subset=None, currency='USD', locale=None, **kwargs):
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
                                currency=currency, 
                                **kwargs)

        if locale is not None:
            return add_formatter(locale=locale)
        else:
            return add_formatter(locale=self.DEFAULT_LOCALE)

    def as_unit(self, unit, subset=None, precision=None, location='prefix', **kwargs):
        """Represent subset of dataframe as a special unit.

        Parameters:
        -----------
        :param unit: string representing unit to be used.
        :param subset: Pandas slice to convert to percentages
        :param precision: int
            Number of decimal places to round to
        :param location: 'prefix' or 'suffix' indicating where the currency symbol
            should be.
        """
        precision = self.precision if precision is None else precision

        return self._format_cells(as_unit,
                                  subset=subset,
                                  precision=precision,
                                  unit=unit,
                                  location=location, 
                                  **kwargs)


    def as_money(self,
                 subset=None,
                 precision=None,
                 currency='$',
                 location='prefix', 
                 **kwargs):
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
                                      location=location, 
                                      **kwargs)

    def _format_cells(self, func, subset=None, **kwargs):
        """Add formatting function to cells."""

        if self.replace_all_nans_with is not None and 'replace_nan_with' not in kwargs:
            kwargs = dict(replace_nan_with = self.replace_all_nans_with, **kwargs)

        # Create function closure for formatting operation
        def fn(*args):
            return func(*args, **kwargs)

        self.formatters.append(Formatter(subset=subset, function=fn))
        return self

    def _apply_formatters(self):
        """Apply all added formatting."""
        for subset, function in self.formatters:
            if subset is None:
                subset = self.data.index
            else:
                subset = _non_reducing_slice(subset)
            self.data.loc[subset] = self.data.loc[subset].applymap(function)
        return self

    def _apply_summaries(self):
        """Add all summary rows and columns."""
        colnames = list(self.data.columns)
        summary_colnames = [series.columns[0] for series in self.summary_cols]
        summary_rownames = [series.index[0] for series in self.summary_rows]

        rows, cols = self.data.shape
        ix_rows = self.data.index.size
        ix_cols = len(self.data.index.names)

        # Add summary rows and columns
        self.data = pd.concat([self.data] + self.summary_cols,
                              axis=1,
                              ignore_index=False)
        self.data = pd.concat([self.data] + self.summary_rows,
                              axis=0,
                              ignore_index=False)

        # Update CSS styles
        for i, _ in enumerate(self.summary_rows):
            index = rows + i + 1
            self._append_selector('tr:nth-child({})'.format(index),
                                  *self.SUMMARY_PROPERTIES)

        for i, _ in enumerate(self.summary_cols):
            index = cols + ix_cols + i + 1
            self._append_selector('td:nth-child({})'.format(index),
                                  *self.SUMMARY_PROPERTIES)

        # Sort column names
        self.data = self.data[colnames + summary_colnames]

        # Fix shared summary cells to be empty
        for row, col in product(summary_rownames, summary_colnames):
            self.data.loc[row, col] = ''

        return self

    def _translate(self):
        """Apply styles and formats before rendering."""
        data = self.data.copy()

        self._apply_summaries()
        self._apply_formatters()
        result = super(self.__class__, self)._translate()

        # Revert changes to inner data
        self.data = data
        
        if self.replace_all_nans_with is not None:
            for row in result['body']:
                for cell in row:
                    v = cell['value']
                    if isinstance(v, Number) and np.isnan(v):
                        cell['value'] = self.replace_all_nans_with 
        return result
