from numbers import Number, Integral
from functools import partial
import locale
import warnings

from babel import Locale, numbers


LOCALE, ENCODING = locale.getlocale()
LOCALE_OBJ = Locale(LOCALE or "en_US")


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
    :param v: numerical value to be converted
    :param precision: int
        decimal places to round to
    """
    if not isinstance(precision, Integral):
        raise TypeError("Precision must be an integer.")

    return format_number(v, "0.{}%".format(precision))


def as_unit(v, unit, precision=2, location='suffix'):
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
        formatter = partial(format_number, prefix=unit)
    elif location == 'suffix':
        formatter = partial(format_number, suffix=unit)
    else:
        raise ValueError("location must be either 'prefix' or 'suffix'.")

    return formatter(v, "0.{}f".format(precision))


as_percent = partial(numbers.format_percent,
                     locale=LOCALE_OBJ)
"""Format number as percentage."""

as_currency = partial(numbers.format_currency,
                      currency='USD',
                      locale=LOCALE_OBJ)
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
