# Depreciation Method

## Introduction

Many [depreciation methods](https://en.wikipedia.org/wiki/Depreciation) are used in accounting.
For example, Straight-line, sum-of-years-digit, Diminishing balance method, etc.
Gernerally, the basic depreciation period in accounting is month.
That means depreciation expenses of every month are identical if we use straight-line method.
However, in this plugin, the basic depreciation period is day and depreciation transactions are generated monthly.
That means day is the implicit period when calculating present value, while month is the explicit period to generate transactions.

## Linear

Linear method is the same with straight-line method.
The present value of assets vs elapsed days is like this:

$$
y=-\frac{p-q}{n}x+p
$$

where $y$ is the present value, $p$ is the original value, $q$ is the residual value, $n$ is the useful life in days and $x$ is the elapsed time in days.

<figure markdown>
  ![linear](./images/linear.png)
  <figcaption>Present value divided by original value of <b>linear</b> method</figcaption>
</figure>

!!! note

    ```
    2020-03-31 * ""
        Assets:Cash                     -600.00 CNY
        Assets:Wealth:Fixed-Assets        1 LENS {600.00 CNY, 2020-03-31, "Nikon"}
            useful_life: "3m"
            residual_value: 200
    ```

    The syntax above equals

    ```
    2020-03-31 * ""
        Assets:Cash                     -600.00 CNY                                   
        Assets:Wealth:Fixed-Assets        1 LENS {600.00 CNY, 2020-03-31, "Nikon"}
            useful_life: "3m"
            residual_value: 200

    2020-04-30 * "auto_depreciation:Nikon"
        Assets:Wealth:Fixed-Assets            -1 LENS {600.00 CNY, 2020-03-31, "Nikon"}
        Assets:Wealth:Fixed-Assets             1 LENS {468 CNY, 2020-04-30, "Nikon"}   
        Expenses:Property-Expenses:Depreciation  132 CNY                                   

    2020-05-31 * "auto_depreciation:Nikon"
        Assets:Wealth:Fixed-Assets            -1 LENS {468 CNY, 2020-04-30, "Nikon"}
        Assets:Wealth:Fixed-Assets             1 LENS {332 CNY, 2020-05-31, "Nikon"}
        Expenses:Property-Expenses:Depreciation  136 CNY                                

    2020-06-30 * "auto_depreciation:Nikon"
        Assets:Wealth:Fixed-Assets            -1 LENS {332 CNY, 2020-05-31, "Nikon"}
        Assets:Wealth:Fixed-Assets             1 LENS {200 CNY, 2020-06-30, "Nikon"}
        Expenses:Property-Expenses:Depreciation  132 CNY
    ```

    Here we can see, the depreciation expenses in May is a little bit greater than that in April and June.
    That's because the present value is a function of useful life in days instead of in months.

## Parabola

Parabola method is the default method and it is the continuous form of sum-of-years-digit method.
The depreciation rate in sum-of-years-digit method decrease linearly.
Therefore, in the continuous form, the present value curve should be a parabola.

$$
y=\frac{p-q}{n^2}(x-n)^2+q
$$

<figure markdown>
  ![parabola](./images/parabola.png)
  <figcaption>Present value divided by original value of <b>parabola</b> method</figcaption>
</figure>