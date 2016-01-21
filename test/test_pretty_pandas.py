import copy
from operator import itemgetter

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


def test_data_safety(dataframe):
    df1 = copy.deepcopy(dataframe)

    df = PrettyPandas(dataframe)
    df.total()._translate()

    assert all(dataframe == df1)
    assert all(df.data == df1)


def test_summary(dataframe):
    p1 = PrettyPandas(dataframe).total()
    actual = list(p1.data.sum())

    r = p1._translate()
    row = [cell for cell in r['body'][10] if cell['type'] == 'td']
    values = [cell['value'] for cell in sorted(row, key=itemgetter('id'))]

    assert values == actual


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

    output = PrettyPandas(df.set_index(['A', 'B'])).total(axis=1)._translate()

    for row in output['body']:
        assert row[-1]['value'] == 10

    for style in output['table_styles']:
        if style['selector'] == 'td:nth-child(5)':
            assert True
            break
    else:
        assert False


def test_as_percent(prettyframe):
    p = prettyframe.as_percent()._translate()

    cells = []
    for row in p['body']:
        values = [cell['value'] for cell in row if cell['type'] == 'td']
        cells.extend(values)

    assert all(c.endswith('%') for c in cells)


def test_as_currency(prettyframe):
    p = prettyframe.as_currency(locale='en_US', currency='USD')._translate()

    cells = []
    for row in p['body']:
        values = [cell['value'] for cell in row if cell['type'] == 'td']
        cells.extend(values)

    assert all(c.startswith('$') or c.startswith('-$') for c in cells)


def test_as_money(prettyframe):
    p = prettyframe.as_money()._translate()

    cells = []
    for row in p['body']:
        values = [cell['value'] for cell in row if cell['type'] == 'td']
        cells.extend(values)

    assert all(c.startswith('$') for c in cells)


def test_as_unit(prettyframe):
    p = prettyframe.as_unit('cm', location='suffix')._translate()

    cells = []
    for row in p['body']:
        values = [cell['value'] for cell in row if cell['type'] == 'td']
        cells.extend(values)

    assert all(c.endswith('cm') for c in cells)
