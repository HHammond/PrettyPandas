from numbers import Number, Integral
from functools import partial


def format_number(v, number_format, prefix='', suffix=''):
    """Format a number to a string."""
    if isinstance(v, Number):
        return ("{{}}{{:{}}}{{}}"
                .format(number_format)
                .format(prefix, v, suffix))
    else:
        raise TypeError("Numberic type required.")


def as_percent(v, precision=2):
    """Convert number to percentage string.

    Parameters:
    -----------
    v: numerical value to be converted
    precision: int
        decimal places to round to
    """
    if not isinstance(precision, Integral):
        raise TypeError("Precision must be an integer.")

    return format_number(v, "0.{}%".format(precision))


def as_unit(v, unit, precision=2, location='suffix'):
    """Convert value to unit.

    Parameters:
    -----------
    v: numerical value
    unit: string of unit
    precision: int
        decimal places to round to
    location:
        'prefix' or 'suffix' representing where the currency symbol falls
        relative to the value
    """
    if not isinstance(precision, Integral):
        raise TypeError("Precision must be an integer.")

    if location == 'prefix':
        formatter = partial(format_number, prefix=unit)
    elif location == 'suffix':
        formatter = partial(format_number, suffix=unit)
    else:
        raise ValueError("location must be either 'prefix' or 'suffix'.")

    return formatter(v, "0.{}f".format(precision))


def as_money(v, precision=2, currency='$', location='prefix'):
    """Convert value to currency.

    Parameters:
    -----------
    v: numerical value
    precision: int
        decimal places to round to
    currency: string representing currency
    location:
        'prefix' or 'suffix' representing where the currency symbol falls
        relative to the value
    """
    return as_unit(v, currency, precision=precision, location=location)
