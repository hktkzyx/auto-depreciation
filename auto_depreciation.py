"""Fixed assets depreciation plugin for beancount."""
import re
from collections import namedtuple

from beancount import loader
from beancount.core import account, amount, convert, data
from beancount.core.number import Decimal
from beancount.parser import printer
from dateutil.relativedelta import relativedelta

__plugins__ = ['auto_depreciation']
__author__ = 'hktkzyx <hktkzyx@qq.com>'

AutoDepreciationError = namedtuple('AutoDepreciationError',
                                   'source message entry')


def auto_depreciation(entries, options_map, config=None):
    """Depreciate fixed assets automatically.

    Please refer to `Beancount Scripting & Plugins <http://furius.ca/beancount/doc/scripting>`_
    for more details.
    
    Parameters
    ----------
    entries
        A list of entry instance.
    options_map
        A dict of options parsed from the file.
    config : str
        A string of plugin configuration.
    
    Returns
    -------
    entries
        A list of processed entries.
    errors
        Error information.
    """
    errors = []
    DEFAULT_ASSETS_ACCOUNT = 'Assets:Wealth:Fixed-Assets'
    DEFAULT_EXPENSES_ACCOUNT = 'Expenses:Property-Expenses:Depreciation'
    DEFAULT_METHOD = 'parabola'
    DEFAULT_RESIDUAL_VALUE = 0.0
    try:
        config_dict = eval(config)
    except (TypeError, SyntaxError):
        config_dict = {}
    try:
        assets_account = config_dict['assets']
    except KeyError:
        assets_account = DEFAULT_ASSETS_ACCOUNT
    if not account.is_valid(assets_account):
        assets_account = DEFAULT_ASSETS_ACCOUNT
    try:
        expenses_account = config_dict['expenses']
    except KeyError:
        expenses_account = DEFAULT_EXPENSES_ACCOUNT
    if not account.is_valid(expenses_account):
        expenses_account = DEFAULT_EXPENSES_ACCOUNT
    try:
        method = config_dict['method']
    except KeyError:
        method = DEFAULT_METHOD

    depreciation_entries = []
    for entry in entries:
        if isinstance(entry, data.Transaction):
            for posting in entry.postings:
                if (posting.meta and 'useful_life' in posting.meta
                        and posting.account == assets_account):
                    cost = posting.cost
                    currency = cost.currency
                    original_value = float(cost.number)
                    try:
                        end_value = float(posting.meta['residual_value'])
                    except KeyError:
                        end_value = DEFAULT_RESIDUAL_VALUE
                    label = cost.label
                    buy_date = cost.date
                    m = re.match(r'([0-9]+)([my])',
                                 str.lower(posting.meta['useful_life']))
                    months_or_years = m.group(2)
                    months = int(m.group(1))
                    if months_or_years == 'y':
                        months = 12 * months
                    dates_list, current_values, depreciation_values \
                        = depreciation_list(original_value, end_value, buy_date, months, method)
                    latest_pos = posting
                    for i, date in enumerate(dates_list):
                        pos_sell = _posting_to_sell(latest_pos)
                        pos_buy = _posting_to_buy(latest_pos, date,
                                                  current_values[i])
                        pos_expense = _posting_to_expense(
                            latest_pos, expenses_account,
                            depreciation_values[i], currency)
                        latest_pos = pos_buy
                        new_pos = [pos_sell, pos_buy, pos_expense]
                        depreciation_entries.append(
                            _auto_entry(entry, date, label, *new_pos))
    new_entries = entries + depreciation_entries
    new_entries.sort(key=data.entry_sortkey)
    return new_entries, errors


def depreciation_list(start_value, end_value, buy_date, months, method):
    """Get depreciation values.
    
    Parameters
    ----------
    start_value : float
        Original value.
    end_value : float
        residual value.
    buy_date : datetime.date
        The date you buy the assets.
    months : int
        Useful life in months.
    
    Returns
    -------
    dates_list : List[datetime.date]
        Forcasted depreciation dates.
    current_values : List[float]
        Present values at corresponging dates in `dates_list`.
    depreciation_values : List[float]
        Depreciation values at corresponging dates in `dates_list`.
    """
    methods = {
        'parabola': parabola,
        'linear': linear,
    }
    get_current_value = methods[method]
    dates_list = [
        buy_date + relativedelta(months=x) for x in range(1, months + 1)
    ]
    days_list = [(x - buy_date).days for x in dates_list]
    depreciation_days = days_list[-1]
    current_values = [
        get_current_value(x, start_value, end_value, depreciation_days)
        for x in days_list
    ]
    depreciation_values = []
    for i, value in enumerate(current_values):
        previous_value = current_values[i - 1] if not i == 0 else start_value
        depreciation_values.append(previous_value - value)
    return dates_list, current_values, depreciation_values


def parabola(x, start_value, end_value, days):
    """Return present value by using parabola method.
    
    Parameters
    ----------
    x : int
        Days after buying the assets.
    start_value : float
        Original value.
    end_value : float
        Residual value.
    days : int
        Useful life in days.
    
    Returns
    -------
    int
        Present value after buying `x` days.
    """
    a = (start_value - end_value) / days**2
    b = -2 * (start_value - end_value) / days
    c = start_value
    return round(a * x**2 + b * x + c)


def linear(x, start_value, end_value, days):
    """Return present value by using linear method.
    
    Parameters
    ----------
    x : int
        Days after buying the assets.
    start_value : float
        Original value.
    end_value : float
        Residual value.
    days : int
        Useful life in days.
    
    Returns
    -------
    int
        Present value after buying `x` days.
    """
    k = -(start_value - end_value) / days
    b = start_value
    return round(k * x + b)


def _posting_to_sell(pos):
    """Return a posting to sell fixed assets.
    
    Parameters
    ----------
    pos
        A instance of posting.
    """
    units = convert.get_units(pos)
    new_units = amount.mul(units, Decimal(-1))
    new_meta = pos.meta.copy()
    try:
        del new_meta['useful_life']
        del new_meta['residual_value']
    except KeyError:
        pass
    return pos._replace(units=new_units, meta=new_meta)


def _posting_to_buy(pos, date, value):
    """Return a posting to buy fixed assets.
    
    Parameters
    ----------
    pos
        The posting to be sold.
    date : datetime.date
        Transaction date.
    value : float
        Cost value.
    """
    cost = pos.cost
    new_cost = cost._replace(date=date, number=Decimal(value))
    new_meta = pos.meta.copy()
    try:
        del new_meta['useful_life']
        del new_meta['residual_value']
    except KeyError:
        pass
    return pos._replace(cost=new_cost, meta=new_meta)


def _posting_to_expense(pos, account, value, currency):
    """Return the expenses posting.
    
    Parameters
    ----------
    pos
        Posting to be sold.
    account : str
        Expenses account name.
    value : float
        Depreciation value.
    currency : str
        Depreciation currency.
    """
    units = amount.Amount(pos.units.number * Decimal(value), currency)
    new_meta = pos.meta.copy()
    try:
        del new_meta['useful_life']
        del new_meta['residual_value']
    except KeyError:
        pass
    return pos._replace(account=account, units=units, cost=None, meta=new_meta)


def _auto_entry(entry, date, label, *args):
    """Return the depreciation entry.
    
    Parameters
    ----------
    entry
        The entry of buying fixed assets.
    date : datetime.date
        Transaction date.
    label : str, None
        Label in inventory.
    *args
        Posting instances in this entry.
    """
    narration = entry.narration
    if narration and label:
        new_narration = ''.join(
            [entry.narration, '-auto_depreciation:', label])
    elif narration:
        new_narration = entry.narration + '-auto_depreciation'
    elif label:
        new_narration = 'auto_depreciation:' + label
    else:
        new_narration = 'auto_depreciation'
    return entry._replace(date=date, narration=new_narration,
                          postings=list(args))


if __name__ == "__main__":
    filename = 'sample.beancount'
    entries, errors, options = loader.load_file(filename)
    printer.print_entries(entries)
