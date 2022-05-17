import textwrap

from beancount import loader
from beancount.parser import cmptest


def test_auto_depreciation():
    sample = """
    plugin "auto_depreciation.depreciation" "{
      'assets':'Assets:Fixed-Assets',
      'expenses':'Expenses:Depreciation',
    }"

    2020-03-01 open Assets:Cash CNY
    2020-03-01 open Assets:Fixed-Assets
    2020-03-01 open Expenses:Depreciation
    2020-03-01 open Equity:Opening-Balances

    2020-03-01 commodity LENS
        name: "Camera lens"
        assets-class: "fixed assets"

    2020-03-01 * ""
        Assets:Cash                     2000.00 CNY
        Equity:Opening-Balances

    2020-03-31 * "Test"
        Assets:Cash                     -2000.00 CNY
        Assets:Fixed-Assets        2 LENS {600.00 CNY, "Nikon"}
          useful_life: "3m"
          residual_value: 200.004
        Assets:Fixed-Assets        1 LENS {800.00 CNY}
          useful_life: "2m"
          other_meta: "other meta"
    """
    entries, errors, _ = loader.load_string(textwrap.dedent(sample))
    expected_entries = """
    2020-03-01 open Assets:Cash                                     CNY
    2020-03-01 open Assets:Fixed-Assets
    2020-03-01 open Expenses:Depreciation
    2020-03-01 open Equity:Opening-Balances

    2020-03-01 commodity LENS
      assets-class: "fixed assets"
      name: "Camera lens"

    2020-03-01 *
      Assets:Cash               2000.00 CNY
      Equity:Opening-Balances  -2000.00 CNY

    2020-03-31 * "Test"
      Assets:Cash              -2000.00 CNY
      Assets:Fixed-Assets        2 LENS {600.00 CNY, 2020-03-31, "Nikon"}
        useful_life: "3m"
        residual_value: 200.004
      Assets:Fixed-Assets        1 LENS {800.00 CNY, 2020-03-31}
        useful_life: "2m"
        other_meta: "other meta"

    2020-04-30 * "Test-auto_depreciation:Nikon"
      Assets:Fixed-Assets   -2 LENS {600.00 CNY, 2020-03-31, "Nikon"}
      Assets:Fixed-Assets    2 LENS {379.74 CNY, 2020-04-30, "Nikon"}
      Expenses:Depreciation    440.52 CNY

    2020-04-30 * "Test-auto_depreciation"
      Assets:Fixed-Assets            -1 LENS {800.00 CNY, 2020-03-31}
        other_meta: "other meta"
      Assets:Fixed-Assets             1 LENS {206.61 CNY, 2020-04-30}
        other_meta: "other meta"
      Expenses:Depreciation  593.39 CNY
        other_meta: "other meta"

    2020-05-31 * "Test-auto_depreciation:Nikon"
      Assets:Fixed-Assets   -2 LENS {379.74 CNY, 2020-04-30, "Nikon"}
      Assets:Fixed-Assets    2 LENS {243.47 CNY, 2020-05-31, "Nikon"}
      Expenses:Depreciation    272.54 CNY

    2020-05-31 * "Test-auto_depreciation"
      Assets:Fixed-Assets            -1 LENS {206.61 CNY, 2020-04-30}
        other_meta: "other meta"
      Assets:Fixed-Assets             1 LENS {0 CNY, 2020-05-31}
        other_meta: "other meta"
      Expenses:Depreciation  206.61 CNY
        other_meta: "other meta"

    2020-06-30 * "Test-auto_depreciation:Nikon"
      Assets:Fixed-Assets  -2 LENS {243.47 CNY, 2020-05-31, "Nikon"}
      Assets:Fixed-Assets   2 LENS {200 CNY, 2020-06-30, "Nikon"}
      Expenses:Depreciation    86.94 CNY

    """
    cmptest.assertEqualEntries(expected_entries, entries)
    assert not errors


def test_rounding_errors():
    sample = """
    plugin "auto_depreciation.depreciation" "{
      'assets':'Assets:Fixed-Assets',
      'expenses':'Expenses:Depreciation',
    }"

    2020-03-01 open Assets:Cash CNY
    2020-03-01 open Assets:Fixed-Assets
    2020-03-01 open Expenses:Depreciation
    2020-03-01 open Equity:Opening-Balances

    2020-03-01 commodity LENS
        name: "Camera lens"
        assets-class: "fixed assets"

    2020-03-01 * ""
        Assets:Cash                     2999.85 CNY
        Equity:Opening-Balances

    2020-03-31 * "Test"
        Assets:Cash                     -2999.85 CNY
        Assets:Fixed-Assets        3 LENS {999.95 CNY, "Nikon"}
          useful_life: "3m"
          residual_value: 200.05
    """
    entries, errors, _ = loader.load_string(textwrap.dedent(sample))
    expected_entries = """
    2020-03-01 open Assets:Cash                                     CNY
    2020-03-01 open Assets:Fixed-Assets
    2020-03-01 open Expenses:Depreciation
    2020-03-01 open Equity:Opening-Balances

    2020-03-01 commodity LENS
      assets-class: "fixed assets"
      name: "Camera lens"

    2020-03-01 *
      Assets:Cash               2999.85 CNY
      Equity:Opening-Balances  -2999.85 CNY

    2020-03-31 * "Test"
      Assets:Cash              -2999.85 CNY
      Assets:Fixed-Assets        3 LENS {999.95 CNY, 2020-03-31, "Nikon"}
        useful_life: "3m"
        residual_value: 200.05

    2020-04-30 * "Test-auto_depreciation:Nikon"
      Assets:Fixed-Assets   -3 LENS {999.95 CNY, 2020-03-31, "Nikon"}
      Assets:Fixed-Assets    3 LENS {559.48 CNY, 2020-04-30, "Nikon"}
      Expenses:Depreciation    1321.41 CNY

    2020-05-31 * "Test-auto_depreciation:Nikon"
      Assets:Fixed-Assets   -3 LENS {559.48 CNY, 2020-04-30, "Nikon"}
      Assets:Fixed-Assets    3 LENS {286.99 CNY, 2020-05-31, "Nikon"}
      Expenses:Depreciation    817.47 CNY

    2020-06-30 * "Test-auto_depreciation:Nikon"
      Assets:Fixed-Assets  -3 LENS {286.99 CNY, 2020-05-31, "Nikon"}
      Assets:Fixed-Assets   3 LENS {200.05 CNY, 2020-06-30, "Nikon"}
      Expenses:Depreciation    260.82 CNY

    """
    cmptest.assertEqualEntries(expected_entries, entries)
    assert not errors
