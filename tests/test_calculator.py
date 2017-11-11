# -*- coding: utf-8 -*-
from __future__ import print_function
import unittest
from datetime import datetime
import decimal
from moneyed import Money, USD
from moneyed.localization import format_money
from mortgagekit.calculator import *


class TestMortgageCalculator(unittest.TestCase):

    def setUp(self):
        # DEVELOPER NOTES:
        # - The above numbers will result in:
        #     - Mortgage Amount: $200,000.00
        #     - Property Value: $250,000.00
        #     - Total Monthly Payment: $1,052.04
        #     - Loan To Value Ratio: 80.00%
        # - Verified by third party tool:
        #     - http://mortgagecalculatorcanada.com/en/calculators/mortgage-payment-calculator/

        self.calc = MortgageCalculator(
            total_amount=Money(amount=250000.00, currency="USD"),
            down_payment_amount=Money(amount=50000.00, currency="USD"),
            amortization_year=25,
            annual_interest_rate=Decimal(0.04),
            payment_frequency=MORTGAGEKIT_MONTH,
            compounding_period=MORTGAGEKIT_SEMI_ANNUAL,
            first_payment_date='2008-01-01'
        )

    def test_init(self):
        # Case 1
        self.assertIsNotNone(self.calc)

        # Case 2
        try:
            calc = MortgageCalculator(
               total_amount=Money(amount=250000.00, currency="USD"),
                down_payment_amount=Money(amount=50000.00, currency="USD"),
                amortization_year=25,
                annual_interest_rate=Decimal(0.04),
                payment_frequency=MORTGAGEKIT_MONTH,
                compounding_period=MORTGAGEKIT_SEMI_ANNUAL,
                first_payment_date=1234
            )
        except Exception as e:
            self.assertIsNotNone(e)

        # Case 3
        calc = MortgageCalculator(
            total_amount=Money(amount=250000.00, currency="USD"),
            down_payment_amount=Money(amount=50000.00, currency="USD"),
            amortization_year=25,
            annual_interest_rate=Decimal(0.04),
            payment_frequency=MORTGAGEKIT_MONTH,
            compounding_period=MORTGAGEKIT_SEMI_ANNUAL,
            first_payment_date=datetime.now()
        )

    def test_get_payment_frequency(self):
        payment_frequency = self.calc.get_payment_frequency()
        self.assertIsNotNone(payment_frequency)
        self.assertEqual(payment_frequency, MORTGAGEKIT_MONTH)

    def test_get_percent_of_loan_financed(self):
        # Test 1
        percent_of_loan_financed = self.calc.get_percent_of_loan_financed()
        self.assertIsNotNone(percent_of_loan_financed)
        self.assertEqual(percent_of_loan_financed, Decimal(80.0))

        # Test 2 - Lets override to get the other conditions.
        self.calc._total_amount = 0
        percent_of_loan_financed = self.calc.get_percent_of_loan_financed()
        self.assertIsNotNone(percent_of_loan_financed)
        self.assertEqual(percent_of_loan_financed, Decimal(0.0))

    def test_get_interest_rate_per_payment_frequency(self):
        # Verify "get_interest_rate_per_payment_frequency" function.
        r = self.calc.get_interest_rate_per_payment_frequency()
        self.assertAlmostEqual(r, 0.0033, 4)

    def test_get_total_number_of_payments_per_frequency(self):
        n = self.calc.get_total_number_of_payments_per_frequency()
        self.assertEqual(n, 300)

    def test_get_mortgage_payment_per_payment_frequency(self):
        # Base case - Try the default computation vierfying no exceptions.
        monthly_payment = self.calc.get_mortgage_payment_per_payment_frequency()
        self.assertIsNotNone(monthly_payment)
        expected = Money(amount=1052.04, currency='USD')
        self.assertAlmostEqual(monthly_payment.amount, expected.amount, 2)

        # Alternate case - Try to divide by zero and verify no exception.
        self.calc._amortization_year = 0
        monthly_payment = self.calc.get_mortgage_payment_per_payment_frequency()
        self.assertIsNotNone(monthly_payment)
        expected = Money(amount=0.00, currency='USD')
        self.assertAlmostEqual(monthly_payment.amount, expected.amount, 2)

    def test_get_mortgage_payment_schedule(self):
        # Verify "get_mortgage_payment_schedule" function.
        payment_schedule = self.calc.get_mortgage_payment_schedule()
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

    def test_get_monthly_mortgage_payment(self):
        # Monthly mortgage payment.
        x = Money(amount=1052.04, currency='USD')
        monthly_mortgage_payment = self.calc.get_monthly_mortgage_payment()
        self.assertAlmostEqual(monthly_mortgage_payment.amount,  x.amount, 2)

    def test_get_annual_mortgage_payment(self):
        annual_mortgage_payment = self.calc.get_annual_mortgage_payment()
        expected = Money(amount=12624.48, currency='USD')
        self.assertAlmostEqual(annual_mortgage_payment.amount,  expected.amount, 2)

if __name__ == '__main__':
    unittest.main()

# Developers Note:
# Third Party Tools to Compare:
# (1) Income Property Evaluator in Apple App Store
# (2) http://mortgagecalculatorcanada.com/en/calculators/mortgage-payment-calculator/
