# py-mortgagekit
## Build Status
[![Build Status](https://travis-ci.org/MikaSoftware/py-mortgagekit.svg?branch=master)](https://travis-ci.org/MikaSoftware/py-mortgagekit)

## Description
Python library for mortgage calculations.

## Build Instructions
1. Clone the project.

  ```bash
  git clone https://github.com/mikasoftware/py-mortgagekit.git
  ```

2. Setup our virtual environment

  ```bash
  virtualenv -p python3.6 env
  ```

3. Activate virtual environment

  ```bash
  source env/bin/activate
  ```

4. Install the dependencies for this project.

  ```bash
  pip install -r requirements.txt
  ```

## Usage
### Development
Here is an example of using the using the library in your code.

  ```python
  from mortgagekit.calculator import *
  from mortgagekit.utils import *

  # Define our variables.
  total_amount = 250000
  down_payment = 50000
  amortization_year = 25
  annual_interest_rate = 0.04
  payment_frequency = MORTGAGEKIT_MONTH # see mortgagekit.py for more options.
  compounding_period = MORTGAGEKIT_SEMI_ANNUAL
  first_payment_date = '2008-01-01'

  # Load up our calculator.
  calc = MortgageCalculator(total_amount, down_payment, amortization_year,
               annual_interest_rate, payment_frequency, compounding_period,
               first_payment_date)

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
python test_mortgagekit.py
```

#### Code Coverage
Here is how you run code coverage. The first command runs the code coverage
and the second command provides a report. If you would like to know more about ``coverage`` then click to [here to read](http://coverage.readthedocs.io/en/latest/).

```bash
coverage run test_mortgagekit.py
coverage report -m mortgagekit.py
```

## License
This library is licensed under the **BSD** license. See [LICENSE.md](LICENSE.md) for more information.
