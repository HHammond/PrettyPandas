from __future__ import unicode_literals

import copy

import pytest
import numpy as np
import pandas as pd

from six import string_types
from prettypandas import PrettyPandas


@pytest.fixture()
def dataframe():
    np.random.seed(24)
    df = pd.DataFrame({
        'A': np.linspace(1, 10, 10),
        'B': np.random.normal(10, 4),
        'C': np.random.normal(10, 4),
        'D': np.random.normal(10, 4),
    })
    return df


@pytest.fixture()
def series(dataframe):
    return dataframe.A


@pytest.fixture()
def prettyframe(dataframe):
    return PrettyPandas(dataframe)


def test_creation(dataframe):
    PrettyPandas(dataframe)

    try:
        PrettyPandas(None)
    except TypeError:
        assert True

    p1 = PrettyPandas(dataframe)
    assert p1._summary_rows == []
    assert p1._summary_cols == []
    assert p1._formatters == []

    p2 = PrettyPandas(dataframe, summary_rows=['test'])
    assert p2._summary_rows == ['test']
    assert p1._summary_cols == []
    assert p1._formatters == []


def test_data_safety(dataframe):
    df1 = copy.deepcopy(dataframe)

    df = PrettyPandas(dataframe)
    df.total()._apply_summaries()

    assert all(dataframe == df1)
    assert all(df._data == df1)


def test_summary(dataframe):
    p1 = PrettyPandas(dataframe).total()
    actual = list(p1._data.sum())

    r = p1._apply_summaries()
    row = r.iloc[-1]
    assert (row == actual).all()


def test_summary_fns(dataframe):
    PrettyPandas(dataframe).total()
    PrettyPandas(dataframe).average()
    PrettyPandas(dataframe).median()
    PrettyPandas(dataframe).max()
    PrettyPandas(dataframe).min()

    out = PrettyPandas(dataframe).total()
    assert len(out._summary_rows) == 1
    assert len(out._summary_cols) == 0

    out = PrettyPandas(dataframe).total(axis=1)
    assert len(out._summary_rows) == 0
    assert len(out._summary_cols) == 1

    out = PrettyPandas(dataframe).total(axis=None)
    assert len(out._summary_rows) == 1
    assert len(out._summary_cols) == 1

    out = PrettyPandas(dataframe).min().max()
    assert len(out._summary_rows) == 2
    assert len(out._summary_cols) == 0

    out = PrettyPandas(dataframe).min().max(axis=1)
    assert len(out._summary_rows) == 1
    assert len(out._summary_cols) == 1


def test_mulitindex():
    df = pd.DataFrame({'A': [1, 2],
                       'B': [3, 4],
                       'D': [4, 3],
                       'C': [6, 7]})

    with pytest.raises(ValueError):
        PrettyPandas(df.set_index(['A', 'B'])).total(axis=1)._apply_summaries()


def test_series_works(series):
    PrettyPandas(series).total()
    assert True


def test_summaries_are_applied_in_order(dataframe):
    df = dataframe.summarize
    N = 100

    for i in range(N):
        df = df.total()
    df = df.to_frame()

    generated_columns = [
        c for c in df.index
        if isinstance(c, string_types) and c.startswith('Total')
    ]

    expected_columns = (
        ['Total']
        + ['Total {}'.format(i + 1) for i in range(1, N)]
    )

    assert generated_columns == expected_columns


def test_pandas_extension(dataframe, series):
    ext_df = dataframe.summarize.total()
    normal_df = PrettyPandas(dataframe).total()

    pd.testing.assert_frame_equal(
        ext_df.to_frame(),
        normal_df.to_frame()
    )

    ext_s = series.summarize.total()
    normal_s = PrettyPandas(series).total()
    pd.testing.assert_frame_equal(
        ext_s.to_frame(),
        normal_s.to_frame()
    )
