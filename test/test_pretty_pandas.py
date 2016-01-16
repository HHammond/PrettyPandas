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

    p1 = PrettyPandas(dataframe, precision=2)
    assert p1.precision == 2
    assert p1.summary_rows == []
    assert p1.summary_cols == []
    assert p1.formatters == []

    p2 = PrettyPandas(dataframe, summary_rows=['test'])
    assert p2.summary_rows == ['test']
    assert p1.summary_cols == []
    assert p1.formatters == []


def test_summary(dataframe):
    df = PrettyPandas(dataframe)

    s1 = df.total(axis=0)
    s1._translate()
    total = dataframe.sum(axis=0)
    assert list(s1.data.ix['Total'].values) == list(total.values)

    s2 = df.total(axis=1)
    s2._translate()
    total = dataframe.apply(np.sum, axis=1)
    assert [v for v in s2.data['Total'] if v != ''] == list(total)


def test_data_safety(dataframe):
    df1 = copy.deepcopy(dataframe)

    df = PrettyPandas(dataframe)
    df.total()._translate()

    assert all(dataframe == df1)


def test_summary_fns(prettyframe):
    prettyframe.total()
    prettyframe.average()
    prettyframe.median()
    prettyframe.max()
    prettyframe.min()

    prettyframe.total(axis=1)
    prettyframe.average(axis=1)
    prettyframe.median(axis=1)
    prettyframe.max(axis=1)
    prettyframe.min(axis=1)

    prettyframe.total(axis=None)
    prettyframe.average(axis=None)
    prettyframe.median(axis=None)
    prettyframe.max(axis=None)
    prettyframe.min(axis=None)
