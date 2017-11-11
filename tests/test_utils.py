# -*- coding: utf-8 -*-
from __future__ import print_function
import unittest
from datetime import datetime
import decimal
from moneyed import Money, USD
from moneyed.localization import format_money
from mortgagekit.utils import *


class TestUtils(unittest.TestCase):

    def setUp(self):
        self.mortgage_payment = Money(amount=666.00, currency="USD")

    def test_get_mortgage_payment_per_frequency_to_per_month(self):
        self.assertIsNotNone(self.mortgage_payment)

        # Annual.
        actual = get_mortgage_payment_per_frequency_to_per_month(self.mortgage_payment, MORTGAGEKIT_ANNUAL)
        expected = Money(amount=55.50, currency="USD")
        self.assertAlmostEqual(actual.amount, expected.amount, 2)

        # Semi-Annual.
        actual = get_mortgage_payment_per_frequency_to_per_month(self.mortgage_payment, MORTGAGEKIT_SEMI_ANNUAL)
        expected = Money(amount=111.00, currency="USD")
        self.assertAlmostEqual(actual.amount, expected.amount, 2)

        # Quarterly.
        actual = get_mortgage_payment_per_frequency_to_per_month(self.mortgage_payment, MORTGAGEKIT_QUARTER)
        expected = Money(amount=166.50, currency="USD")
        self.assertAlmostEqual(actual.amount, expected.amount, 2)

        # Bi-Monthly.
        actual = get_mortgage_payment_per_frequency_to_per_month(self.mortgage_payment, MORTGAGEKIT_BI_MONTH)
        expected = Money(amount=333.00, currency="USD")
        self.assertAlmostEqual(actual.amount, expected.amount, 2)

        # Monthly.
        actual = get_mortgage_payment_per_frequency_to_per_month(self.mortgage_payment, MORTGAGEKIT_MONTH)
        expected = Money(amount=666.00, currency="USD")
        self.assertAlmostEqual(actual.amount, expected.amount, 2)

        # Bi-Weekly.
        actual = get_mortgage_payment_per_frequency_to_per_month(self.mortgage_payment, MORTGAGEKIT_BI_WEEK)
        expected = Money(amount=1443.00, currency="USD")
        self.assertAlmostEqual(actual.amount, expected.amount, 2)

        # Weekly.
        actual = get_mortgage_payment_per_frequency_to_per_month(self.mortgage_payment, MORTGAGEKIT_WEEK)
        expected = Money(amount=2886.00, currency="USD")
        self.assertAlmostEqual(actual.amount, expected.amount, 2)

        # Exception.
        try:
            get_mortgage_payment_per_frequency_to_per_month(self.mortgage_payment, Decimal(666))
        except Exception as e:
            self.assertIn("ERROR: Unsupported payment frequency type!", str(e))

    def test_get_mortgage_payment_per_frequency_to_per_annual(self):
        self.assertIsNotNone(self.mortgage_payment)

        # Annual.
        actual = get_mortgage_payment_per_frequency_to_per_annual(self.mortgage_payment, MORTGAGEKIT_ANNUAL)
        expected = Money(amount=666.00, currency="USD")
        self.assertAlmostEqual(actual.amount, expected.amount, 2)

        # Semi-Annual.
        actual = get_mortgage_payment_per_frequency_to_per_annual(self.mortgage_payment, MORTGAGEKIT_SEMI_ANNUAL)
        expected = Money(amount=1332.00, currency="USD")
        self.assertAlmostEqual(actual.amount, expected.amount, 2)

        # Quarterly.
        actual = get_mortgage_payment_per_frequency_to_per_annual(self.mortgage_payment, MORTGAGEKIT_QUARTER)
        expected = Money(amount=2664.00, currency="USD")
        self.assertAlmostEqual(actual.amount, expected.amount, 2)

        # Bi-Monthly.
        actual = get_mortgage_payment_per_frequency_to_per_annual(self.mortgage_payment, MORTGAGEKIT_BI_MONTH)
        expected = Money(amount=3996.00, currency="USD")
        self.assertAlmostEqual(actual.amount, expected.amount, 2)

        # Monthly.
        actual = get_mortgage_payment_per_frequency_to_per_annual(self.mortgage_payment, MORTGAGEKIT_MONTH)
        expected = Money(amount=7992.00, currency="USD")
        self.assertAlmostEqual(actual.amount, expected.amount, 2)

        # Bi-Weekly.
        actual = get_mortgage_payment_per_frequency_to_per_annual(self.mortgage_payment, MORTGAGEKIT_BI_WEEK)
        expected = Money(amount=17316.00, currency="USD")
        self.assertAlmostEqual(actual.amount, expected.amount, 2)

        # Weekly.
        actual = get_mortgage_payment_per_frequency_to_per_annual(self.mortgage_payment, MORTGAGEKIT_WEEK)
        expected = Money(amount=34632.00, currency="USD")
        self.assertAlmostEqual(actual.amount, expected.amount, 2)

        # Exception.
        try:
            get_mortgage_payment_per_frequency_to_per_annual(self.mortgage_payment, Decimal(666))
        except Exception as e:
            self.assertIn("ERROR: Unsupported payment frequency type!", str(e))

    def test_get_next_date_by_frequency(self):
        test_datetime = datetime(2008, 1, 1, 0, 0, 0, 00)

        # Annual.
        actual = get_next_date_by_frequency(test_datetime, MORTGAGEKIT_ANNUAL)
        expected = datetime(2009, 1, 1, 0, 0, 0, 00)
        self.assertEqual(actual, expected)

        # Semi-Annual.
        actual = get_next_date_by_frequency(test_datetime, MORTGAGEKIT_SEMI_ANNUAL)
        expected = datetime(2008, 7, 1, 0, 0, 0, 00)
        self.assertEqual(actual, expected)

        # Quarterly.
        actual = get_next_date_by_frequency(test_datetime, MORTGAGEKIT_QUARTER)
        expected = datetime(2008, 5, 1, 0, 0, 0, 00)
        self.assertEqual(actual, expected)

        # Bi-Monthly.
        actual = get_next_date_by_frequency(test_datetime, MORTGAGEKIT_BI_MONTH)
        expected = datetime(2008, 3, 1, 0, 0, 0, 00)
        self.assertEqual(actual, expected)

        # Monthly.
        actual = get_next_date_by_frequency(test_datetime, MORTGAGEKIT_MONTH)
        expected = datetime(2008, 2, 1, 0, 0, 0, 00)
        self.assertEqual(actual, expected)

        # Bi-Weekly.
        actual = get_next_date_by_frequency(test_datetime, MORTGAGEKIT_BI_WEEK)
        expected = datetime(2008, 1, 15, 0, 0, 0, 00)
        self.assertEqual(actual, expected)

        # Weekly.
        actual = get_next_date_by_frequency(test_datetime, MORTGAGEKIT_WEEK)
        expected = datetime(2008, 1, 8, 0, 0, 0, 00)
        self.assertEqual(actual, expected)

        # Exception.
        try:
            get_next_date_by_frequency(test_datetime, Decimal(666.00))
        except Exception as e:
            self.assertIn("ERROR: Unsupported payment frequency type!", str(e))
