import copy

import pytest
import numpy as np
import pandas as pd

from prettypandas import PrettyPandas


@pytest.fixture()
def dataframe():
    np.random.seed(24)
    df = pd.DataFrame({'A': np.linspace(1, 10, 10)})
    df = pd.concat([df, pd.DataFrame(np.random.randn(10, 4),
                                     columns=list('BCDE'))],
                   axis=1)
    return df


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
    assert p1.summary_rows == []
    assert p1.summary_cols == []
    assert p1.formatters == []

    p2 = PrettyPandas(dataframe, summary_rows=['test'])
    assert p2.summary_rows == ['test']
    assert p1.summary_cols == []
    assert p1.formatters == []


def test_data_safety(dataframe):
    df1 = copy.deepcopy(dataframe)

    df = PrettyPandas(dataframe)
    df.total()._apply_summaries()

    assert all(dataframe == df1)
    assert all(df.data == df1)


def test_summary(dataframe):
    p1 = PrettyPandas(dataframe).total()
    actual = list(p1.data.sum())

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
    assert len(out.summary_rows) == 1
    assert len(out.summary_cols) == 0

    out = PrettyPandas(dataframe).total(axis=1)
    assert len(out.summary_rows) == 0
    assert len(out.summary_cols) == 1

    out = PrettyPandas(dataframe).total(axis=None)
    assert len(out.summary_rows) == 1
    assert len(out.summary_cols) == 1

    out = PrettyPandas(dataframe).min().max()
    assert len(out.summary_rows) == 2
    assert len(out.summary_cols) == 0

    out = PrettyPandas(dataframe).min().max(axis=1)
    assert len(out.summary_rows) == 1
    assert len(out.summary_cols) == 1


def test_mulitindex():
    df = pd.DataFrame({'A': [1, 2],
                       'B': [3, 4],
                       'D': [4, 3],
                       'C': [6, 7]})

    with pytest.raises(ValueError):
        output = PrettyPandas(df.set_index(['A', 'B'])).total(axis=1)._apply_summaries()
