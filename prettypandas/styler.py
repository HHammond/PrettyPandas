from __future__ import unicode_literals

from IPython.display import HTML
from pandas.core.indexing import _non_reducing_slice
import pandas as pd

if pd.__version__ >= '0.20.0':
    from pandas.io.formats.style import Styler
elif pd.__version__ >= '0.18.1':
    from pandas.formats.style import Styler
else:
    from pandas.core.style import Styler

import numpy as np

from copy import copy
from collections import namedtuple, OrderedDict
from itertools import product
from functools import partial
from operator import methodcaller
import warnings


Formatter = namedtuple("Formatter", "subset, function")


def axis_is_rows(axis):
    return axis == 0 or axis == 'rows'


def axis_is_cols(axis):
    return axis == 1 or axis == 'columns'


class Aggregate(object):

    def __init__(self, title, func, subset=None, axis=0, raw=False, *args, **kwargs):
        self.title = title
        self.subset = subset
        self.axis = axis
        self.raw = raw

        self.func = func
        self.args = args
        self.kwargs = kwargs

    def apply(self, df):

        if self.subset:
            if axis_is_rows(self.axis):
                df = df[self.subset]
            if axis_is_cols(self.axis):
                df = df.loc[self.subset]

        result = df.agg(self.func, axis=self.axis, *self.args, **self.kwargs)
        result.name = self.title
        return result


class PrettyPandas(object):
    """Pretty pandas dataframe Styles.

    Parameters
    ----------
    :param data: Series or DataFrame
    :param summary_rows:
        list of single-row dataframes to be appended as a summary
    :param summary_cols:
        list of single-row dataframes to be appended as a summary
    """

    def __init__(self,
                 data,
                 summary_rows=None,
                 summary_cols=None,
                 formatters=None,
                 *args,
                 **kwargs):

        self.data = data
        self.summary_rows = summary_rows or []
        self.summary_cols = summary_cols or []
        self.formatters = formatters or []

    def _copy(self):
        return self.__class__(
            self.data,
            summary_rows=self.summary_rows[:],
            summary_cols=self.summary_cols[:],
            formatters=self.formatters[:],
        )

    def _add_summary(self, agg):
        new = self._copy()

        if axis_is_rows(agg.axis):
            new.summary_rows += [agg]

        elif axis_is_cols(agg.axis):
            new.summary_cols += [agg]

        else:
            raise ValueError("Invalid axis supplied.")

        return new

    @classmethod
    def set_locale(cls, locale):
        """Set the PrettyPandas default locale."""
        cls.DEFAULT_LOCALE = locale

    def summary(self, func=methodcaller('sum'), title='Total', axis=0, subset=None, *args, **kwargs):
        """Add multiple summary rows or columns to the dataframe.

        Parameters
        ----------
        :param func: function to be used for a summary.
        :param titles: Title for this summary column.
        :param axis:
            Same as numpy and pandas axis argument. A value of None will cause
            the summary to be applied to both rows and columns.
        :param args: Positional arguments passed to all the functions.
        :param kwargs: Keyword arguments passed to all the functions.

        The results of summary can be chained together.
        """

        if axis is None:
            return (
                self
                .summary(func=func, title=title, axis=0, subset=subset, *args, **kwargs)
                .summary(func=func, title=title, axis=1, subset=subset, *args, **kwargs)
            )
        else:
            agg = Aggregate(title, func, subset=subset, axis=axis, *args, **kwargs)
            return self._add_summary(agg)

    def total(self, title="Total", **kwargs):
        """Add a total summary to this table.

        :param title: Title to be displayed.
        :param kwargs: Keyword arguments passed to ``numpy.sum``.
        """
        return self.summary(methodcaller('sum'), title, **kwargs)

    def average(self, title="Average", **kwargs):
        """Add a mean summary to this table.

        :param title: Title to be displayed.
        :param kwargs: Keyword arguments passed to ``numpy.mean``.
        """
        return self.summary(methodcaller('mean'), title, **kwargs)

    def median(self, title="Median", **kwargs):
        """Add a median summary to this table.

        :param title: Title to be displayed.
        :param kwargs: Keyword arguments passed to ``numpy.median``.
        """
        return self.summary(methodcaller('median'), title, **kwargs)

    def max(self, title="Maximum", **kwargs):
        """Add a maximum summary to this table.

        :param title: Title to be displayed.
        :param kwargs: Keyword arguments passed to ``numpy.max``.
        """
        return self.summary(methodcaller('max'), title, **kwargs)

    def min(self, title="Minimum", **kwargs):
        """Add a minimum summary to this table.

        :param title: Title to be displayed.
        :param kwargs: Keyword arguments passed to ``numpy.min``.
        """
        return self.summary(methodcaller('min'), title, **kwargs)

    def _cleaned_aggregates(self, summaries):
        titles = set()
        for agg in summaries:
            title = agg.title
            i = 1
            while agg.title in titles:
                agg.title = "{}_{}".format(title, i)
                i += 1

            titles.add(agg.title)
            yield agg

    @property
    def _cleaned_summary_rows(self):
        return list(self._cleaned_aggregates(self.summary_rows))

    @property
    def _cleaned_summary_cols(self):
        return list(self._cleaned_aggregates(self.summary_cols))

    def _apply_summaries(self):
        """Add all summary rows and columns."""

        as_frame = lambda r: r.to_frame() if isinstance(r, pd.Series) else r

        df = self.data

        if df.index.nlevels > 1:
            raise ValueError("You cannot currently have both summary rows and columns on a MultiIndex.")

        _df = df
        if self.summary_rows:
            rows = pd.concat([agg.apply(_df) for agg in self._cleaned_summary_rows], axis=1).T
            df = pd.concat([df, as_frame(rows)], axis=0)

        if self.summary_cols:
            cols = pd.concat([agg.apply(_df) for agg in self._cleaned_summary_cols], axis=1)
            df = pd.concat([df, as_frame(cols)], axis=1)

        return df

    def to_frame(self):
        return self._apply_summaries()

    @property
    def style(self):
        row_titles = [a.title for a in self._cleaned_summary_rows]
        col_titles = [a.title for a in self._cleaned_summary_cols]
        common = pd.IndexSlice[row_titles, col_titles]
        row_ix = pd.IndexSlice[row_titles, :]
        col_ix = pd.IndexSlice[:, col_titles]

        def handle_na(df):
            df.loc[col_ix] = df.loc[col_ix].fillna('')
            df.loc[row_ix] = df.loc[row_ix].fillna('')
            return df

        return (
            self._apply_summaries()
            .pipe(handle_na)
            .style
            .applymap(lambda r: 'font-weight: 900', subset=row_ix)
            .applymap(lambda r: 'font-weight: 900', subset=col_ix)
        )

    def render(self):
        return self.style.render()

    def _repr_html_(self):
        return self.render()
