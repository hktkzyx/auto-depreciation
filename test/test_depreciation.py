import textwrap
import unittest

from beancount import loader
from beancount.parser import cmptest


class TestExampleAutoDepreciation(cmptest.TestCase):

    def test_auto_depreciation(self):
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
              residual_value: 200
            Assets:Fixed-Assets        1 LENS {800.00 CNY}
              useful_life: "2m"
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
            residual_value: 200
          Assets:Fixed-Assets        1 LENS {800.00 CNY, 2020-03-31}
            useful_life: "2m"

        2020-04-30 * "Test-auto_depreciation:Nikon"
          Assets:Fixed-Assets   -2 LENS {600.00 CNY, 2020-03-31, "Nikon"}
          Assets:Fixed-Assets    2 LENS {380 CNY, 2020-04-30, "Nikon"}
          Expenses:Depreciation    440.00 CNY

        2020-04-30 * "Test-auto_depreciation"
          Assets:Fixed-Assets            -1 LENS {800.00 CNY, 2020-03-31}
          Assets:Fixed-Assets             1 LENS {207 CNY, 2020-04-30}
          Expenses:Depreciation  593.00 CNY

        2020-05-31 * "Test-auto_depreciation:Nikon"
          Assets:Fixed-Assets   -2 LENS {380 CNY, 2020-04-30, "Nikon"}
          Assets:Fixed-Assets    2 LENS {243 CNY, 2020-05-31, "Nikon"}
          Expenses:Depreciation    274 CNY

        2020-05-31 * "Test-auto_depreciation"
          Assets:Fixed-Assets            -1 LENS {207 CNY, 2020-04-30}
          Assets:Fixed-Assets             1 LENS {0 CNY, 2020-05-31}
          Expenses:Depreciation  207 CNY
        
        2020-06-30 * "Test-auto_depreciation:Nikon"
          Assets:Fixed-Assets  -2 LENS {243 CNY, 2020-05-31, "Nikon"}
          Assets:Fixed-Assets   2 LENS {200 CNY, 2020-06-30, "Nikon"}
          Expenses:Depreciation    86 CNY

        """
        self.assertEqualEntries(expected_entries, entries)
        self.assertFalse(errors)

    def test_rounding_errors(self):
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
          Assets:Fixed-Assets    3 LENS {559 CNY, 2020-04-30, "Nikon"}
          Expenses:Depreciation    1322.85 CNY

        2020-05-31 * "Test-auto_depreciation:Nikon"
          Assets:Fixed-Assets   -3 LENS {559 CNY, 2020-04-30, "Nikon"}
          Assets:Fixed-Assets    3 LENS {287 CNY, 2020-05-31, "Nikon"}
          Expenses:Depreciation    816 CNY

        2020-06-30 * "Test-auto_depreciation:Nikon"
          Assets:Fixed-Assets  -3 LENS {287 CNY, 2020-05-31, "Nikon"}
          Assets:Fixed-Assets   3 LENS {200 CNY, 2020-06-30, "Nikon"}
          Expenses:Depreciation    261 CNY

        """
        self.assertEqualEntries(expected_entries, entries)
        self.assertFalse(errors)


if __name__ == "__main__":
    unittest.main()
