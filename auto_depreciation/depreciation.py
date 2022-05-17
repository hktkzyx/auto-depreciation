from collections import namedtuple
import datetime
import re
from typing import Optional

from beancount import loader
from beancount.core import account
from beancount.core import amount
from beancount.core import convert
from beancount.core import data
from beancount.core import number
from beancount.parser import printer
from dateutil import relativedelta

__plugins__ = ['auto_depreciation']
__author__ = 'hktkzyx <hktkzyx@qq.com>'

AutoDepreciationError = namedtuple('AutoDepreciationError',
                                   'source message entry')


def read_assets_account_from_config(config) -> str:
    """Return assets account.

    Parameters
    ----------
    config : str
        A string of plugin configuration.

    Returns
    -------
    account : str
        An account.

    Examples
    --------
    >>> read_assets_account_from_config("{'assets': 'Assets:Wealth'}")
    'Assets:Wealth'
    >>> read_assets_account_from_config(None)
    'Assets:Wealth:Fixed-Assets'
    >>> read_assets_account_from_config("{'assets': 'Assets-fafdWealth'}")
    'Assets:Wealth:Fixed-Assets'
    """
    default_account = 'Assets:Wealth:Fixed-Assets'
    try:
        config_dict = eval(config)
    except (TypeError, SyntaxError):
        config_dict = {}
    result_account = config_dict.get('assets', default_account)
    if not account.is_valid(result_account):
        result_account = default_account
    return result_account


def read_expenses_account_from_config(config) -> str:
    """Return expenses account.

    Parameters
    ----------
    config : str
        A string of plugin configuration.

    Returns
    -------
    account : str
        An account.

    Examples
    --------
    >>> read_expenses_account_from_config("{'expenses': 'Expenses:Depreciation'}")
    'Expenses:Depreciation'
    >>> read_expenses_account_from_config(None)
    'Expenses:Property-Expenses:Depreciation'
    >>> read_expenses_account_from_config("{'expenses': 'falsjfowfowe-fsdf!'}")
    'Expenses:Property-Expenses:Depreciation'
    """
    default_account = 'Expenses:Property-Expenses:Depreciation'
    try:
        config_dict = eval(config)
    except (TypeError, SyntaxError):
        config_dict = {}
    result_account = config_dict.get('expenses', default_account)
    if not account.is_valid(result_account):
        result_account = default_account
    return result_account


def read_depreciation_method_from_config(config) -> str:
    """Return depreciation method.

    Parameters
    ----------
    config : str
        A string of plugin configuration.

    Returns
    -------
    method : str
        A method.

    Examples
    --------
    >>> read_depreciation_method_from_config("{'method': 'linear'}")
    'linear'
    >>> read_depreciation_method_from_config(None)
    'parabola'
    """
    try:
        config_dict = eval(config)
    except (TypeError, SyntaxError):
        config_dict = {}
    return config_dict.get('method', 'parabola')


def parse_useful_life_in_months(posting: data.Posting) -> int:
    """Return useful life in months.

    Parameters
    ----------
    posting : data.Posting
        A posting instance.

    Returns
    -------
    months : int
        Useful life in months.
    """
    matched = re.match(r'(\d+)([my])', str.lower(posting.meta['useful_life']))
    months_or_years = matched[2]
    value = int(matched[1])
    return 12 * value if months_or_years == 'y' else value


def parse_residual_value(posting: data.Posting) -> number.Decimal:
    """Return the residual value.

    Parameters
    ----------
    posting : data.Posting
        A posting instance.

    Returns
    -------
    residual_value : number.Decimal
        Residual value.
    """
    value = posting.meta.get('residual_value', 0)
    return number.D(round(value * 100)) / number.D(100)


def is_posting_a_depreciation(posting: data.Posting,
                              depreciation_assets_account: str) -> bool:
    """Return whether the posting is a depreciation one."""
    return (posting.meta and 'useful_life' in posting.meta
            and posting.account == depreciation_assets_account)


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
    assets_account = read_assets_account_from_config(config)
    expenses_account = read_expenses_account_from_config(config)
    method = read_depreciation_method_from_config(config)

    forecasted_entries = []
    for entry in entries:
        if isinstance(entry, data.Transaction):
            forecasted_entries = forecasted_entries + create_forecasted_depreciation_entries(
                entry, assets_account, expenses_account, method)
    result_entries = entries + forecasted_entries
    result_entries.sort(key=data.entry_sortkey)
    return result_entries, errors


def create_forecasted_depreciation_entries(
        entry: data.Transaction,
        assets_account: str,
        expenses_account: str,
        method: str) -> list[data.Transaction]:
    """Return forecasted depreciation entries.

    Parameters
    ----------
    entry : data.Transaction
        A Transaction entry instance.
    assets_account : str
        The assets account.
    expenses_account : str
        The expenses account.
    method : str
        The depreciation method.

    Returns
    -------
    depreciation_entries : list of data.Transaction
        The forecasted depreciation transaction entries.
    """
    if not isinstance(entry, data.Transaction):
        raise TypeError("'entry' must be a transaction.")
    entries = []
    for posting in entry.postings:
        if is_posting_a_depreciation(posting, assets_account):
            months = parse_useful_life_in_months(posting)
            (dates, current_values,
             depreciation_values) = cal_forecasted_depreciation_info(
                 posting, months, method)
            latest_posting = posting
            for (date, present_value,
                 depreciation_value) in zip(dates,
                                            current_values,
                                            depreciation_values):
                sell_posting = create_forecasted_sell_posting(latest_posting)
                buy_posting = create_forecasted_buy_posting(
                    latest_posting, date, present_value)
                expense_posting = create_depreciation_expense_posting(
                    latest_posting, expenses_account, depreciation_value)
                latest_posting = buy_posting
                entries.append(
                    create_depreciation_entry(
                        entry,
                        date,
                        posting.cost.label,
                        [sell_posting, buy_posting, expense_posting]))
    return entries


def cal_forecasted_depreciation_info(
    posting: data.Posting, months: int, method: str
) -> tuple[list[datetime.date], list[number.Decimal], list[number.Decimal]]:
    """Get depreciation values.

    Parameters
    ----------
    posting : data.Posting
        The depreciation posting.
    months : int
        Useful life in months.
    method : str
        Depreciation method.

    Returns
    -------
    forecasted_dates : list of datetime.date
        Forecasted depreciation dates.
    rounded_current_values : list of Decimal
        Present values at corresponding `forecasted_dates`.
    depreciation_values : list of Decimal
        Depreciation values at corresponding `forecasted_dates`.
    """
    methods = {
        'parabola': cal_present_value_by_parabola,
        'linear': cal_present_value_by_linear,
    }
    cal_current_values = methods[method]
    forecasted_dates = [
        posting.cost.date + relativedelta.relativedelta(months=month)
        for month in range(1, months + 1)
    ]
    days = [(x - posting.cost.date).days for x in forecasted_dates]
    current_values = [
        cal_current_values(day,
                           posting.cost.number,
                           parse_residual_value(posting),
                           days[-1]) for day in days
    ]
    rounded_current_values = [
        number.D(round(float(value) * 100)) / number.D(100)
        for value in current_values
    ]
    depreciation_values = []
    for i, value in enumerate(rounded_current_values):
        previous_value = (rounded_current_values[i - 1]
                          if i != 0 else posting.cost.number)
        depreciation_values.append(previous_value - value)
    return forecasted_dates, rounded_current_values, depreciation_values


def cal_present_value_by_parabola(day: int,
                                  start_value: number.Decimal,
                                  end_value: number.Decimal,
                                  days: int) -> number.Decimal:
    """Return present value by using parabola method.

    Parameters
    ----------
    day : int
        Days after buying the assets.
    start_value : number.Decimal
        Original value.
    end_value : number.Decimal
        Residual value.
    days : int
        Useful life in days.

    Returns
    -------
    number.Decimal
        Present value after buying `x` days.
    """
    a = (start_value - end_value) / days**2
    b = -2 * (start_value - end_value) / days
    c = start_value
    return a * day**2 + b * day + c


def cal_present_value_by_linear(day: int,
                                start_value: number.Decimal,
                                end_value: number.Decimal,
                                days: int) -> number.Decimal:
    """Return present value by using linear method.

    Parameters
    ----------
    day : int
        Days after buying the assets.
    start_value : number.Decimal
        Original value.
    end_value : number.Decimal
        Residual value.
    days : int
        Useful life in days.

    Returns
    -------
    number.Decimal
        Present value after buying `x` days.
    """
    k = -(start_value - end_value) / days
    b = start_value
    return k * day + b


def create_forecasted_sell_posting(posting: data.Posting) -> data.Posting:
    """Return a posting to sell fixed assets.

    Parameters
    ----------
    posting : data.Posting
        A instance of posting.

    Returns
    -------
    posting : data.Posting
        A instance of sell posting.
    """
    units = amount.mul(convert.get_units(posting), number.Decimal(-1))
    meta = posting.meta.copy()
    if 'useful_life' in meta:
        del meta['useful_life']
    if 'residual_value' in meta:
        del meta['residual_value']
    return posting._replace(units=units, meta=meta)


def create_forecasted_buy_posting(
        posting: data.Posting, date: datetime.date,
        present_value: number.Decimal) -> data.Posting:
    """Return a posting to buy fixed assets.

    Parameters
    ----------
    posting : data.Posting
        The posting to be sold.
    date : datetime.date
        Transaction date.
    present_value : number.Decimal
        Present value of the fixed assets.

    Returns
    -------
    posting : data.Posting
        A instance of buy posting.
    """
    cost = posting.cost._replace(date=date, number=present_value)
    meta = posting.meta.copy()
    if 'useful_life' in meta:
        del meta['useful_life']
    if 'residual_value' in meta:
        del meta['residual_value']
    return posting._replace(cost=cost, meta=meta)


def create_depreciation_expense_posting(posting: data.Posting,
                                        account: str,
                                        depreciation_value: number.Decimal):
    """Return the expenses posting.

    Parameters
    ----------
    posting : data.Posting
        Posting to be sold.
    account : str
        Expenses account name.
    depreciation_value : number.Decimal
        Depreciation value.

    Returns
    -------
    posting : data.Posting
        A instance of expense posting.
    """
    units = amount.Amount(posting.units.number * depreciation_value,
                          posting.cost.currency)
    meta = posting.meta.copy()
    if 'useful_life' in meta:
        del meta['useful_life']
    if 'residual_value' in meta:
        del meta['residual_value']
    return posting._replace(account=account, units=units, cost=None, meta=meta)


def create_depreciation_entry(entry,
                              date: datetime.date,
                              label: Optional[str],
                              postings: list[data.Posting]):
    """Return the depreciation entry.

    Parameters
    ----------
    entry
        The entry of buying fixed assets.
    date : datetime.date
        Transaction date.
    label : str, None
        Label in inventory.
    postings : list of data.Posting
        Posting instances in this entry.

    Returns
    -------
    entry
        The depreciation entry.
    """
    if entry.narration and label:
        narration = f'{entry.narration}-auto_depreciation:{label}'
    elif entry.narration:
        narration = f'{entry.narration}-auto_depreciation'
    elif label:
        narration = f'auto_depreciation:{label}'
    else:
        narration = 'auto_depreciation'
    return entry._replace(date=date, narration=narration, postings=postings)


if __name__ == "__main__":
    filename = 'sample.beancount'
    entries, errors, options = loader.load_file(filename)
    printer.print_entries(entries)
    printer.print_errors(errors)
