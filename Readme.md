# Pretty Pandas

![Testing Status](https://travis-ci.org/HHammond/PrettyPandas.svg?branch=master)
[![Documentation Status](http://readthedocs.org/projects/prettypandas/badge/?version=latest)](http://prettypandas.readthedocs.org/en/latest/?badge=latest)
![Supported Versions](https://img.shields.io/pypi/pyversions/prettypandas.svg)
![PyPI](https://img.shields.io/pypi/l/prettypandas.svg)

PrettyPandas is a Pandas DataFrame Styler class that helps you create
report quality tables with a simple API.

```{.sourceCode .python}
from prettypandas import PrettyPandas

(
    PrettyPandas(df, precision=3)
    .as_percent(subset=['C'])
    .as_currency(subset=['A', 'B'])
    .total()
    .summary(lambda col: np.sum(col), title='Custom Summary')
)
```

<img src="/docs/source/_static/Images/gh_readme@2x.png" width="500px" />

Features
--------

-   Add summary rows and columns.
-   A nice and customizable theme.
-   Number formatting for currency, scientific units, and percentages.
-   Chaining commands.
-   Works seamlessly with [Pandas Style
    API](http://pandas.pydata.org/pandas-docs/stable/style.html).

Installation
------------

You can install PrettyPandas using `pip` with support for Python 2.7,
3.3, 3.4, and 3.5:

``` {.sourceCode .sh}
pip install prettypandas
```

You can also install from source:

``` {.sourceCode .sh}
git clone git@github.com:HHammond/PrettyPandas.git
cd PrettyPandas
python setup.py install
```

Documentation
-------------

Documentation is hosted on [Read the Docs](http://prettypandas.readthedocs.org).
