# -*- coding: utf-8 -*-
from __future__ import print_function
import unittest
from datetime import datetime
import decimal
from moneyed import Money, USD
from moneyed.localization import format_money
from mortgagekit.calculator import *


class TestMortgageCalculator(unittest.TestCase):

    def test_case_1(self):
        # Set our test data.
        total_amount = Money(amount=250000.00, currency="USD")
        down_payment = Money(amount=50000.00, currency="USD")
        amortization_year = 25
        annual_interest_rate = Decimal(0.04)
        payment_frequency = MORTGAGEKIT_MONTH
        compounding_period = MORTGAGEKIT_SEMI_ANNUAL
        first_payment_date = '2008-01-01'

        # DEVELOPER NOTES:
        # - The above numbers will result in:
        #     - Mortgage Amount: $200,000.00
        #     - Property Value: $250,000.00
        #     - Total Monthly Payment: $1,052.04
        #     - Loan To Value Ratio: 80.00%
        # - Verified by third party tool:
        #     - http://mortgagecalculatorcanada.com/en/calculators/mortgage-payment-calculator/

        # Load up our calculator.
        calc = MortgageCalculator(
            total_amount,
            down_payment,
            amortization_year,
            annual_interest_rate,
            payment_frequency,
            compounding_period,
            first_payment_date
        )

        # Verify our calculator object was generated.
        self.assertIsNotNone(calc)

        # Verify "interest_rate_per_payment_frequency" function.
        r = calc.interest_rate_per_payment_frequency()
        self.assertAlmostEqual(r, 0.0033, 4)

        # Verify "total_number_of_payments_per_frequency" function.
        n = calc.total_number_of_payments_per_frequency()
        self.assertEqual(n, 300)

        # Verify "mortgage_payment_per_payment_frequency" function.
        monthly_payment = calc.mortgage_payment_per_payment_frequency()
        self.assertIsNotNone(monthly_payment)
        x = Money(amount=1052.04, currency='USD')
        self.assertAlmostEqual(monthly_payment.amount, x.amount, 2)

        # Verify "percent_of_loan_financed" function.
        percent = calc.percent_of_loan_financed()
        self.assertEqual(percent, 80.00)

        # Verify "mortgage_payment_schedule" function.
        payment_schedule = calc.mortgage_payment_schedule()
        self.assertIsNotNone(payment_schedule)

        # YEAR 1 | MONTH 1
        interval_01_01  = payment_schedule[0]
        self.assertEqual(interval_01_01['year'], 1)
        self.assertEqual(interval_01_01['interval'], 1)
        self.assertAlmostEqual(interval_01_01['interest'].amount, Money(amount=661.18, currency='USD').amount, 2)
        self.assertAlmostEqual(interval_01_01['principle'].amount,  Money(amount=390.86, currency='USD').amount, 2)
        self.assertAlmostEqual(interval_01_01['loan_balance'].amount,  Money(amount=199609.14, currency='USD').amount, 2)

        # YEAR 1 | MONTH 5
        interval_01_05 = payment_schedule[4]
        self.assertEqual(interval_01_05['year'], 1)
        self.assertEqual(interval_01_05['interval'], 5)
        self.assertAlmostEqual(interval_01_05['interest'].amount, Money(amount=655.98, currency='USD').amount, 2)
        self.assertAlmostEqual(interval_01_05['principle'].amount, Money(amount=396.06, currency='USD').amount, 2)
        self.assertAlmostEqual(interval_01_05['loan_balance'].amount, Money(amount=198032.72, currency='USD').amount, 2)

        # YEAR 25 | MONTH 12
        interval_25  = payment_schedule[299]
        self.assertAlmostEqual(interval_25['year'], 25)
        self.assertAlmostEqual(interval_25['interest'].amount, Money(amount=3.47, currency='USD').amount, 2)
        self.assertAlmostEqual(interval_25['principle'].amount, Money(amount=1048.57, currency='USD').amount, 2)
        self.assertAlmostEqual(interval_25['loan_balance'].amount, Money(amount=0.0, currency='USD').amount, 2)

        # Monthly mortgage payment.
        monthly_mortgage_payment = calc.monthly_mortgage_payment()
        self.assertAlmostEqual(monthly_mortgage_payment.amount,  x.amount, 2)

        # # Annual mortgage payment.
        annual_mortgage_payment = calc.annual_mortgage_payment()
        expected = Money(amount=12624.48, currency='USD')
        self.assertAlmostEqual(annual_mortgage_payment.amount,  expected.amount, 2)


if __name__ == '__main__':
    unittest.main()

# Developers Note:
# Third Party Tools to Compare:
# (1) Income Property Evaluator in Apple App Store
# (2) http://mortgagecalculatorcanada.com/en/calculators/mortgage-payment-calculator/
