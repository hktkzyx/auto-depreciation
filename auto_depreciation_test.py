import textwrap

import unittest
from beancount import loader
from beancount.parser import cmptest


class TestExampleAutoDepreciation(cmptest.TestCase):
    def test_auto_depreciation(self):
        sample = """
        option "insert_pythonpath" "True"
        plugin "auto_depreciation" "{
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
            Assets:Cash                     1000.00 CNY
            Equity:Opening-Balances

        2020-03-31 * "[200, 3m]"
            Assets:Cash                     -600.00 CNY
            Assets:Fixed-Assets        1 LENS {600.00 CNY, "Nikon"}
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
          Assets:Cash               1000.00 CNY
          Equity:Opening-Balances  -1000.00 CNY

        2020-03-31 * "[200, 3m]"
          Assets:Cash              -600.00 CNY                                   
          Assets:Fixed-Assets        1 LENS {600.00 CNY, 2020-03-31, "Nikon"}

        2020-04-30 * "Auto Depreciation:Nikon"
          Assets:Fixed-Assets   -1 LENS {600.00 CNY, 2020-03-31, "Nikon"}
          Assets:Fixed-Assets    1 LENS {380 CNY, 2020-04-30, "Nikon"}   
          Expenses:Depreciation    220 CNY                                   

        2020-05-31 * "Auto Depreciation:Nikon"
          Assets:Fixed-Assets   -1 LENS {380 CNY, 2020-04-30, "Nikon"}
          Assets:Fixed-Assets    1 LENS {243 CNY, 2020-05-31, "Nikon"}
          Expenses:Depreciation    137 CNY                                

        2020-06-30 * "Auto Depreciation:Nikon"
          Assets:Fixed-Assets  -1 LENS {243 CNY, 2020-05-31, "Nikon"}
          Assets:Fixed-Assets   1 LENS {200 CNY, 2020-06-30, "Nikon"}
          Expenses:Depreciation    43 CNY                                

        """
        self.assertEqualEntries(expected_entries, entries)
        self.assertFalse(errors)


if __name__ == "__main__":
    unittest.main()