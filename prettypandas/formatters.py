from numbers import Number, Integral
from functools import partial, wraps
import locale
import warnings

from babel import Locale, numbers


LOCALE, ENCODING = locale.getlocale()
LOCALE_OBJ = Locale(LOCALE or "en_US")


def surpress_formatting_errors(fn):
    """
    I know this is dangerous and the wrong way to solve the problem, but when
    using both row and columns summaries it's easier to just swallow errors
    so users can format their tables how they need.
    """
    @wraps(fn)
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValueError:
            return ""
    return inner


def format_number(number_format, prefix='', suffix=''):
    """Format a number to a string."""
    @surpress_formatting_errors
    def inner(v):
        if isinstance(v, Number):
            return ("{{}}{{:{}}}{{}}"
                    .format(number_format)
                    .format(prefix, v, suffix))
        else:
            raise TypeError("Numberic type required.")
    return inner


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

    return surpress_formatting_errors(
        format_number("0.{}%".format(precision))
    )


def as_unit(unit, precision=2, location='suffix'):
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

    return surpress_formatting_errors(
        formatter("0.{}f".format(precision))
    )


def as_currency(currency='USD', locale=LOCALE_OBJ):
    @surpress_formatting_errors
    def inner(v):
        return numbers.format_currency(v, currency=currency, locale=LOCALE_OBJ)
    return inner

