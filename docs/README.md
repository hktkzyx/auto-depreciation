# Auto Depreciation Plugin

[Auto depreciation](https://hktkzyx.github.io/auto-depreciation/)
is a [beancount](https://github.com/beancount/beancount) plugin to deal with fixed assets depreciation.
In our daily life, we may buy some valuable goods like cars, phones, furniture, etc.
All these transactions are preferred to be documented as transfer instead of expenses,
otherwise, you cannot evaluate your daily expenses properly.
This plugin can generate depreciation transactions automatically.

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/hktkzyx/auto-depreciation/build-and-test)](https://github.com/hktkzyx/auto-depreciation/actions)
[![Codecov](https://img.shields.io/codecov/c/github/hktkzyx/auto-depreciation)](https://app.codecov.io/gh/hktkzyx/auto-depreciation)
[![PyPI](https://img.shields.io/pypi/v/auto-depreciation)](https://pypi.org/project/auto-depreciation/)
[![PyPI - License](https://img.shields.io/pypi/l/auto-depreciation)](https://github.com/hktkzyx/auto-depreciation/blob/master/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/auto-depreciation)](https://pypi.org/project/auto-depreciation/)
[![GitHub last commit](https://img.shields.io/github/last-commit/hktkzyx/auto-depreciation)](https://github.com/hktkzyx/auto-depreciation)

## Installing

```bash
pip install auto-depreciation
```

## Configuration

The parameters passed to the plugin are:

- `assets`: Fixed assets account.
- `expenses`: Depreciation expenses account.
- `method`: Depreciation method.

Parameter default values are as follows:

```
plugin "auto_depreciation.depreciation" "{
    'assets':'Assets:Wealth:Fixed-Assets',
    'expenses':'Expenses:Property-Expenses:Depreciation',
    'method':'parabola',
}"
```

## Usage

Xiaoming is a young man. One day he bought a car and paid in cash.
We assume that the original value of that car is 100,000 CNY
and it will scrap after 10 years.
The residual value is still 1,000 CNY.

He can use this plugin like this:

!!! example

    ```
    plugin "auto_depreciation.depreciation"

    2020-03-01 commodity CARS
        name: "cars"
        assets-class: "fixed assets"

    2020-03-31 * ""
        Assets:Cash                     -100000.00 CNY
        Assets:Wealth:Fixed-Assets           1 CARS {100000.00 CNY, "BMW"}
            useful_life: "10y"
            residual_value: 1000
    ```

where we use metadata attached in the posting to pass residual value and useful life to plugin.

`useful_life` is the compulsory item and `y` represent *years* while `m` represent *months*.

`residual_value` is optional and by default 0.

!!! note

    `residual_value` is rounded to 2 decimal places.

!!! example

    ```
    2020-03-31 * "Example"
        Assets:Cash              -600.00 CNY
        Assets:Wealth:Fixed-Assets        1 LENS {600.00 CNY, "Nikon"}
            useful_life: "3m"
            residual_value: 200
    ```

    The code above is equal to

    ```
    2020-03-31 * "Example"
        Assets:Cash                     -600.00 CNY
        Assets:Wealth:Fixed-Assets        1 LENS {600.00 CNY, 2020-03-31, "Nikon"}
            useful_life: "3m"
            residual_value: 200

    2020-04-30 * "Example-auto_depreciation:Nikon"
        Assets:Wealth:Fixed-Assets              -1 LENS {600.00 CNY, 2020-03-31, "Nikon"}
        Assets:Wealth:Fixed-Assets               1 LENS {379.74 CNY, 2020-04-30, "Nikon"}
        Expenses:Property-Expenses:Depreciation    220.26 CNY

    2020-05-31 * "Example-auto_depreciation:Nikon"
        Assets:Wealth:Fixed-Assets              -1 LENS {379.74 CNY, 2020-04-30, "Nikon"}
        Assets:Wealth:Fixed-Assets               1 LENS {243.47 CNY, 2020-05-31, "Nikon"}
        Expenses:Property-Expenses:Depreciation    136.27 CNY

    2020-06-30 * "Example-auto_depreciation:Nikon"
        Assets:Wealth:Fixed-Assets              -1 LENS {243.47 CNY, 2020-05-31, "Nikon"}
        Assets:Wealth:Fixed-Assets               1 LENS {200 CNY, 2020-06-30, "Nikon"}
        Expenses:Property-Expenses:Depreciation     43.47 CNY
    ```

If the amount of fixed assets is greater than 1, all will be depreciated like this:

!!! example

    ```
    2020-03-31 * "Example"
        Assets:Cash                    -1200.00 CNY
        Assets:Wealth:Fixed-Assets        2 LENS {600.00 CNY, 2020-03-31, "Nikon"}
            useful_life: "3m"
            residual_value: 200

    2020-04-30 * "Example-auto_depreciation:Nikon"
        Assets:Wealth:Fixed-Assets              -2 LENS {600.00 CNY, 2020-03-31, "Nikon"}
        Assets:Wealth:Fixed-Assets               2 LENS {379.74 CNY, 2020-04-30, "Nikon"}
        Expenses:Property-Expenses:Depreciation    440.52 CNY

    ...
    ```
