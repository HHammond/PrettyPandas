from numbers import Number, Integral
from functools import partial
import locale
import warnings
import numpy

from babel import Locale, numbers


LOCALE, ENCODING = locale.getlocale()
LOCALE_OBJ = Locale(LOCALE or "en_US")


def format_number(v, number_format, prefix='', suffix='', replace_nan_with=None):
    """Format a number to a string."""
    if replace_nan_with is not None and numpy.isnan(v):
        return replace_nan_with
        
    if isinstance(v, Number):
        return ("{{}}{{:{}}}{{}}"
                .format(number_format)
                .format(prefix, v, suffix))
    else:
        raise TypeError("Numberic type required.")


def as_percent(v, precision=2, scale_1_as_100_percent = True, **kwargs):
    """Convert number to percentage string.

    Parameters:
    -----------
    :param v: numerical value to be converted
    :param precision: int
        decimal places to round to
    """
    if not isinstance(precision, Integral):
        raise TypeError("Precision must be an integer.")

    if not scale_1_as_100_percent:
        v /= 100.0
    return format_number(v, "0.{}%".format(precision), **kwargs)


def as_unit(v, unit, precision=2, location='suffix', **kwargs):
    """Convert value to unit.

    Parameters:
    -----------
    :param v: numerical value
    :param unit: string of unit
    :param precision: int
        decimal places to round to
    :param location:
        'prefix' or 'suffix' representing where the currency symbol falls
        relative to the value
    """
    if not isinstance(precision, Integral):
        raise TypeError("Precision must be an integer.")

    if location == 'prefix':
        formatter = partial(format_number, prefix=unit, **kwargs)
    elif location == 'suffix':
        formatter = partial(format_number, suffix=unit, **kwargs)
    else:
        raise ValueError("location must be either 'prefix' or 'suffix'.")

    return formatter(v, "0.{}f".format(precision))

#disable use of babel for percentages so we can control precision (not implemented by original author in github repo)
#as_percent = partial(numbers.format_percent,
#                     locale=LOCALE_OBJ)
#"""Format number as percentage."""

def as_currency(val, replace_nan_with = None, *args, **kwargs):
    if replace_nan_with is not None and numpy.isnan(v):
        return replace_nan_with
    return numbers.format_currency(val, currency='USD', locale=LOCALE_OBJ)
"""Format number as currency."""


def as_money(v, precision=2, currency='$', location='prefix'):
    """[DEPRECATED] Convert value to currency.

    Parameters:
    -----------
    :param v: numerical value
    :param precision: int
        decimal places to round to
    :param currency: string representing currency
    :param location:
        'prefix' or 'suffix' representing where the currency symbol falls
        relative to the value
    """
    warnings.warn("Depricated in favour of `as_currency`.",
                  DeprecationWarning)

    return as_unit(v, currency, precision=precision, location=location)
