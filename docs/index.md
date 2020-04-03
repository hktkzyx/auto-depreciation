# Welcome to Auto Depreciation Plugin

`auto_depreciation` is a beancount plugin to deal with fixed assets depreciation.
In our daily life, we may buy some valuable goods like cars, phones, furniture, etc.
All these transactions are preferred to be documented as transfer instead of expenses,
otherwise, you cannot evaluate your daily expenses properly.
This plugin can generate depreciation transactions automatically.

## Installing

Copy the file to your PYTHONPATH.
You can also copy the plugin to the folder which contains the beancount file and add the following lines into your beancount file:

    option "insert_pythonpath" "True"
    plugin "auto_depreciation"

## Configuration

The parameters passed to the plugin are:

- `assets`: Fixed assets account.
- `expenses`: Depreciation expenses account.
- `method`: Depreciation method.

Parameter default values are as follows:

    plugin "auto_depreciation" "{
        'assets':'Assets:Wealth:Fixed-Assets-CNY',
        'expenses':'Expenses:Property-Expenses:Depreciation',
        'method':'parabola',
    }"

## How to use

Xiaoming is a youg man. One day he bought a car and paid in cash.
We assume that the original value of that car is 100,000 CNY
and it will scrap after 10 years.
The residual value is still 1,000 CNY.

He can use this plugin like this:

    option "insert_pythonpath" "True"
    plugin "auto_depreciation"

    2020-03-01 commodity CARS
        name: "cars"
        assets-class: "fixed assets"
    
    2020-03-31 * "Auto Depreciation [1000, 10y]"
        Assets:Cash                     -100000.00 CNY
        Assets:Wealth:Fixed-Assets-CNY           1 CARS {100000.00 CNY, "BMW"}

`[1000, 10y]` in the narration represent residual value and useful life.
`y` represent *years* while `m` represent *months*.

???+ example

        2020-03-31 * "[200, 3m]"
            Assets:Cash              -600.00 CNY
            Assets:Wealth:Fixed-Assets-CNY        1 LENS {600.00 CNY, "Nikon"}

    The code above is equal to

        2020-03-31 * "[200, 3m]"
            Assets:Cash                     -600.00 CNY                                   
            Assets:Wealth:Fixed-Assets-CNY        1 LENS {600.00 CNY, 2020-03-31, "Nikon"}

        2020-04-30 * "Auto Depreciation:Nikon"
            Assets:Wealth:Fixed-Assets-CNY              -1 LENS {600.00 CNY, 2020-03-31, "Nikon"}
            Assets:Wealth:Fixed-Assets-CNY               1 LENS {380 CNY, 2020-04-30, "Nikon"}   
            Expenses:Property-Expenses:Depreciation    220 CNY                                   

        2020-05-31 * "Auto Depreciation:Nikon"
            Assets:Wealth:Fixed-Assets-CNY              -1 LENS {380 CNY, 2020-04-30, "Nikon"}
            Assets:Wealth:Fixed-Assets-CNY               1 LENS {243 CNY, 2020-05-31, "Nikon"}
            Expenses:Property-Expenses:Depreciation    137 CNY                                

        2020-06-30 * "Auto Depreciation:Nikon"
            Assets:Wealth:Fixed-Assets-CNY              -1 LENS {243 CNY, 2020-05-31, "Nikon"}
            Assets:Wealth:Fixed-Assets-CNY               1 LENS {200 CNY, 2020-06-30, "Nikon"}
            Expenses:Property-Expenses:Depreciation     43 CNY                                
