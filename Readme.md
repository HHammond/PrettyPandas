# Pretty Pandas

PrettyPandas uses the new Pandas style API to add beautiful reporting 
functionality to Pandas DataFrames.

## Features:

* Multiple summary rows and columns

* A nice and customizable theme

* Number formatting for currency, scientific units, and percentages

## Usage

Add a simple total:

```
PrettyPandas(df).total()
```

![](screenshots/1.png)

Add an average:

```
PrettyPandas(df).average()
```

![](screenshots/2.png)

Add an average across the table:

```
PrettyPandas(df).average(axis=1)
```

![](screenshots/3.png)

Add an average across and down the table:

```
PrettyPandas(df).average(axis=None)
```

![](screenshots/4.png)

Summaries can be chained together:

```
PrettyPandas(df).min().max()
```

![](screenshots/5.png)

Custom functions can be used for summaries:

```
PrettyPandas(df).summary(np.mean, "Average")
```

![](screenshots/6.png)

### Multiple Summary Functions

Multiple summaries can be applied at the same time using the `multi_summary` 
method.

```
PrettyPandas(df).multi_summary([np.mean, np.sum],
                               ['Average', 'Total'],
                               axis=0)
```

![](screenshots/7.png)


Multiple summaries have the exact same API as regular summaries which means all
the above examples work with no surprises.

### Number Formatting

PrettyPandas has built in support for money, percentages, and units.

```
PrettyPandas(df).as_percent()
```

![](screenshots/8.png)


```
PrettyPandas(df).as_money()
```

![](screenshots/9.png)


```
PrettyPandas(df).as_percent(precision=3)
```

![](screenshots/10.png)


```
PrettyPandas(df).as_money(currency=u"$", precision=3)
```

![](screenshots/11.png)


```
PrettyPandas(df).as_unit('cm', location='suffix')
```

![](screenshots/12.png)


Number formatting conforms to standard Pandas indexing and slicing:

```
PrettyPandas(df).as_percent(subset=['A'])
```

![](screenshots/13.png)


Number formats will be applied to summaries as well. 

```
PrettyPandas(df).as_percent(subset=['A']).total()
```

![](screenshots/15.png)


## Issues

* This class doesn't conform to the regular Styler.export function, which
means at the current time you cannot use the `export` and `style.use`
functions of a dataframe. Instead you can build a function which to
template table styles and use that to clone styles.

* Modifying the underlying dataset uses a copy and ignores any performance
issues. This means applying formats to large dataframes could be slow and
memory could be an issue.

* Summaries which you might want to interact (like the intersection of two
totals) will not be rendered. This is a design decision because most summary
functions don't need to interact don't interact nicely.

* Summary functions don't take a subset argument which means that any
summary will be applied to every column or row.

* Number formatting fails on nulls.
