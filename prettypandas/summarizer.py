from __future__ import unicode_literals

from operator import methodcaller
import pandas as pd
from .formatters import as_percent, as_currency, as_unit, LOCALE_OBJ


def _axis_is_rows(axis):
    return axis == 0 or axis == 'rows'


def _axis_is_cols(axis):
    return axis == 1 or axis == 'columns' or axis == 'index'


class Aggregate(object):
    """Aggreagte

    Wrapper to calculate aggregate row on datafame.

    :param title:
        Aggregate row title
    :param func:
        Function to be passed to DataFrame.agg
    :param subset:
        Subset of DataFrame to compute aggregate on
    :param axis:
        Pandas axis to compute over

    :param args:
        Positionsal arguments to DataFrame.agg
    :param kwargs:
        Keyword arguments to DataFrame.agg
    """

    def __init__(
            self,
            title,
            func,
            subset=None,
            axis=0,
            *args,
            **kwargs):

        self.title = title
        self.subset = subset
        self.axis = axis

        self.func = func
        self.args = args
        self.kwargs = kwargs

    def apply(self, df):
        """Compute aggregate over DataFrame"""

        if self.subset:
            if _axis_is_rows(self.axis):
                df = df[self.subset]
            if _axis_is_cols(self.axis):
                df = df.loc[self.subset]

        result = df.agg(self.func, axis=self.axis, *self.args, **self.kwargs)
        result.name = self.title
        return result


class Formatter(object):
    """Formatter

    Wrapper to apply formatting to datafame.

    :param formatter:
        Function to be passed to Pandas Styler.format
    :param args:
        Positionsal arguments to Styler.format
    :param kwargs:
        Keyword arguments to Styler.format
    """

    def __init__(self, formatter, args, kwargs):
        self.formatter = formatter
        self.args = args
        self.kwargs = kwargs

    def apply(self, styler):
        """Apply Summary over Pandas Styler"""
        return styler.format(self.formatter, *self.args, **self.kwargs)


class PrettyPandas(object):
    """PrettyPandas

    Parameters
    ----------
    :param data: DataFrame.
    :param summary_rows:
        list of Aggregate objects to be appended as a summary.
    :param summary_cols:
        list of Aggregate objects to be appended as a summary.
    :param formatters:
        List of Formatter objects to format.
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

    def _add_formatter(self, formatter):
        new = self._copy()
        new.formatters += [formatter]
        return new

    def _add_summary(self, agg):
        new = self._copy()

        if _axis_is_rows(agg.axis):
            new.summary_rows += [agg]
        elif _axis_is_cols(agg.axis):
            new.summary_cols += [agg]
        else:
            raise ValueError("Invalid axis supplied.")

        return new

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

        def as_frame(r):
            if isinstance(r, pd.Series):
                return r.to_frame()
            else:
                return r

        df = self.data

        if df.index.nlevels > 1:
            raise ValueError(
                "You cannot currently have both summary rows and columns on a "
                "MultiIndex."
            )

        _df = df
        if self.summary_rows:
            rows = pd.concat([agg.apply(_df)
                              for agg in self._cleaned_summary_rows], axis=1).T
            df = pd.concat([df, as_frame(rows)], axis=0)

        if self.summary_cols:
            cols = pd.concat([agg.apply(_df)
                              for agg in self._cleaned_summary_cols], axis=1)
            df = pd.concat([df, as_frame(cols)], axis=1)

        return df

    @property
    def frame(self):
        """Add summaries and convert back to DataFrame"""
        return self._apply_summaries()

    def to_frame(self):
        """Add summaries and convert back to DataFrame"""
        return self.frame

    @property
    def style(self):
        """Add summaries and convert to Pandas Styler"""
        row_titles = [a.title for a in self._cleaned_summary_rows]
        col_titles = [a.title for a in self._cleaned_summary_cols]
        row_ix = pd.IndexSlice[row_titles, :]
        col_ix = pd.IndexSlice[:, col_titles]

        def handle_na(df):
            df.loc[col_ix] = df.loc[col_ix].fillna('')
            df.loc[row_ix] = df.loc[row_ix].fillna('')
            return df

        styler = (
            self
            .frame
            .pipe(handle_na)
            .style
            .applymap(lambda r: 'font-weight: 900', subset=row_ix)
            .applymap(lambda r: 'font-weight: 900', subset=col_ix)
        )

        for formatter in self.formatters:
            styler = formatter.apply(styler)

        return styler

    def render(self):
        return self.style.render()

    def _repr_html_(self):
        return self.style._repr_html_()

    def __str__(self):
        return str(self.frame)

    def __repr__(self):
        return str(self.frame)

    def summary(self,
                func=methodcaller('sum'),
                title='Total',
                axis=0,
                subset=None,
                *args,
                **kwargs):
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
                .summary(
                    func=func,
                    title=title,
                    axis=0,
                    subset=subset,
                    *args,
                    **kwargs
                )
                .summary(
                    func=func,
                    title=title,
                    axis=1,
                    subset=subset,
                    *args,
                    **kwargs
                )
            )
        else:
            agg = Aggregate(title, func, subset=subset,
                            axis=axis, *args, **kwargs)
            return self._add_summary(agg)

    def multi_summary(
            self,
            funcs,
            titles,
            axis=0,
            *args,
            **kwargs):

        new = self
        for f, t in zip(funcs, titles):
            new = new.summary(func=f, title=t, axis=axis, *args, **kwargs)
        return new

    def total(self, title="Total", **kwargs):
        """Add a total summary to this table.

        :param title: Title to be displayed.
        """
        return self.summary(methodcaller('sum'), title, **kwargs)

    def average(self, title="Average", **kwargs):
        """Add a mean summary to this table.

        :param title: Title to be displayed.
        """
        return self.summary(methodcaller('mean'), title, **kwargs)

    def median(self, title="Median", **kwargs):
        """Add a median summary to this table.

        :param title: Title to be displayed.
        """
        return self.summary(methodcaller('median'), title, **kwargs)

    def max(self, title="Maximum", **kwargs):
        """Add a maximum summary to this table.

        :param title: Title to be displayed.
        """
        return self.summary(methodcaller('max'), title, **kwargs)

    def min(self, title="Minimum", **kwargs):
        """Add a minimum summary to this table.

        :param title: Title to be displayed.
        """
        return self.summary(methodcaller('min'), title, **kwargs)

    def as_percent(self, precision=2, *args, **kwargs):
        """Format subset as percentages

        :param precision: Decimal precision
        :param subset: Pandas subset
        """
        f = Formatter(as_percent(precision), args, kwargs)
        return self._add_formatter(f)

    def as_currency(self, currency='USD', locale=LOCALE_OBJ, *args, **kwargs):
        """Format subset as currency

        :param currency: Currency
        :param locale: Babel locale for currency formatting
        :param subset: Pandas subset
        """
        f = Formatter(
            as_currency(currency=currency, locale=locale),
            args,
            kwargs
        )
        return self._add_formatter(f)

    def as_unit(self, unit, location='suffix', *args, **kwargs):
        """Format subset as with units

        :param unit: string to use as unit
        :param location: prefix or suffix
        :param subset: Pandas subset
        """
        f = Formatter(
            as_unit(unit, location=location),
            args,
            kwargs
        )
        return self._add_formatter(f)
