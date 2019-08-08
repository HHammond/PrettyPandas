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
    if replace_nan_with is not None and (v is None or isinstance(v, Number) and numpy.isnan(v)):
        return replace_nan_with
        
    if isinstance(v, Number):
        return ("{}{:%s}{}" % number_format).format(prefix, v, suffix)
    else:
        raise TypeError("Numeric type required.")


def as_percent_with_precision(v, precision=2, scale_1_as_100_percent = True, replace_nan_with=None, **kwargs):
    """Convert number to percentage string.

    Parameters:
    -----------
    :param v: numerical value to be converted
    :param precision: int
        decimal places to round to
    :param scale_1_as_100_percent: boolean
        By default the value 1 is converted to 100%.
        Set this to False to indicate that 100 converts to 100%.
    """
    if not isinstance(precision, Integral):
        raise TypeError("Precision must be an integer.")

    if replace_nan_with is not None and numpy.isnan(v):
        return replace_nan_with

    if scale_1_as_100_percent:
        v *= 100.0

    return format_number(v, ".{}f".format(precision), suffix='%', **kwargs)


def as_unit(v, unit, precision=2, location='suffix', thousands_separator = True, **kwargs):
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

    format_str = ".{}f"
    if thousands_separator:
        format_str = "," + format_str
    return formatter(v, format_str.format(precision))

def as_percent_babel(val, precision = None, *args, **kwargs): 
    """Format number as percentage using babel."""
    #n.b. swallow the precision parameter as we can't pass it to format_percent
    return numbers.format_percent(val, locale=LOCALE_OBJ, *args, **kwargs)


PERCENT_FORMATTERS = dict(
    format_fn = as_percent_babel,
    formatters = dict(
        as_percent_babel = as_percent_babel,
        as_percent_with_precision = as_percent_with_precision
    )
)

def as_currency(val, replace_nan_with = None, *args, **kwargs):
    if replace_nan_with is not None and numpy.isnan(val):
        return replace_nan_with
    return numbers.format_currency(val, currency='USD', locale=LOCALE_OBJ)
"""Format number as currency."""


def as_money(v, precision=2, currency='$', location='prefix', *args, **kwargs):
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
    return as_unit(v, currency, precision=precision, location=location, *args, **kwargs)
