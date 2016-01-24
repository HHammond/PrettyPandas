from IPython.display import HTML

from .styler import PrettyPandas
from .sparklines import Sparkline


def apply_pretty_globals():
    """Apply global CSS to make dataframes pretty.

    This function injects HTML and CSS code into the notebook in order to make
    tables look pretty. Third party hosts of notebooks advise against using
    this and some don't support it. As long as you are okay with HTML injection
    in your notebook, go ahead and use this. Otherwise use the ``PrettyPandas``
    class.
    """
    return HTML("""
        <style type='text/css'>
            /* Pretty Pandas Dataframes */
            .dataframe * {border-color: #c0c0c0 !important;}
            .dataframe th{background: #eee;}
            .dataframe td{
                background: #fff;
                text-align: right;
                min-width:5em;
            }

            /* Format summary rows */
            .dataframe-summary-row tr:last-child,
            .dataframe-summary-col td:last-child{
                background: #eee;
                font-weight: 500;
            }
        </style>
        """)


__all__ = ['PrettyPandas',
           'apply_pretty_globals',
           'Sparkline']
