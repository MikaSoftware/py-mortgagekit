# py-mortgagekit
## Build Status
[![Build Status](https://travis-ci.org/MikaSoftware/py-mortgagekit.svg?branch=master)](https://travis-ci.org/MikaSoftware/py-mortgagekit)
[![PyPI version fury.io](https://badge.fury.io/py/py-mortgagekit.svg)](https://pypi.python.org/pypi/py-mortgagekit)
[![Coverage Status](https://coveralls.io/repos/github/MikaSoftware/py-mortgagekit/badge.svg?branch=master)](https://coveralls.io/github/MikaSoftware/py-mortgagekit?branch=master)

## Description
Python library for mortgage calculations.

## Installation
### Requirements
* Python 3.6++

### Instructions
  ```bash
  pip instll py-mortgagekit
  ```

## Usage
### Development
Here is an example of using the using the library in your code.

  ```python
  from mortgagekit.constants import *
  from mortgagekit.calculator import *

  # Define our variables.
  total_amount = Money(amount=250000.00, currency="USD")
  down_payment = Money(amount=50000.00, currency="USD")
  amortization_year = 25
  annual_interest_rate = Decimal(0.04)
  payment_frequency = MORTGAGEKIT_MONTH # see calculator.py for more options.
  compounding_period = MORTGAGEKIT_SEMI_ANNUAL
  first_payment_date = '2008-01-01'

  # Feel free to use an alternate currency type by first checking to see if your
  # your currency is supported here:
  # https://github.com/limist/py-moneyed/blob/master/moneyed/localization.py#L348
  currency='USD'

  # Load up our calculator.
  calc = MortgageCalculator(total_amount, down_payment, amortization_year,
               annual_interest_rate, payment_frequency, compounding_period,
               first_payment_date, currency)

  # Perform computations.
  payment_schedule = calc.mortgage_payment_schedule()

  # You can now inspect the results and use it for your purposes.
  print(payment_schedule)
  ```

### Quality Assurance
#### Unit Tests
If you want to run the unit tests, you can run the following.

Here is how you run the unit tests.

```bash
python setup.py test
```

#### Code Coverage
Here is how you run code coverage. The first command runs the code coverage
and the second command provides a report. If you would like to know more about ``coverage`` then click to [here to read](http://coverage.readthedocs.io/en/latest/).

```bash
coverage run --source=mortgagekit setup.py test
coverage report -m
```

## License
This library is licensed under the **BSD** license. See [LICENSE.md](LICENSE.md) for more information.
