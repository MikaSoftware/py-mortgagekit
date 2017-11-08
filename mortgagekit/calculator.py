# -*- coding: utf-8 -*-
"""
API library for mortgage calculations.
See README for more details.
"""

from __future__ import print_function
import sys
import argparse
from datetime import datetime, timedelta
from decimal import Decimal
import math
from dateutil.relativedelta import relativedelta
from moneyed import Money, USD
from moneyed.localization import format_money


__author__ = "Bartlomiej Mika"
__copyright__ = "Copyright (c) 2017, Mika Software Corporation"
__credits__ = ["Bartlomiej Mika", "David Stubbs"]
__license__ = "BSD 2-Clause License"
__version__ = "1.0.2a1"
__maintainer__ = "Mika Software Corporation"
__email = "bart@mikasoftware.com"
__status__ = "Production"


MORTGAGEKIT_ANNUAL = Decimal(1)
MORTGAGEKIT_SEMI_ANNUAL = Decimal(2)
MORTGAGEKIT_QUARTER = Decimal(4)
MORTGAGEKIT_BI_MONTH = Decimal(6)
MORTGAGEKIT_MONTH = Decimal(12)
MORTGAGEKIT_BI_WEEK = Decimal(26)
MORTGAGEKIT_WEEK = Decimal(52)


class MortgageCalculator(object):
    """
    Class used to calculate mortgage payments schedule.
    """
    def __init__(self, total_amount, down_payment_amount, amortization_year,
                 annual_interest_rate, payment_frequency, compounding_period,
                 first_payment_date, currency='USD'):

        # Perform assertions to ensure input is standardized by programmers
        # who use this library.
        assert isinstance(total_amount, Money), 'total_amount is not a Money class: %r' % total_amount
        assert isinstance(down_payment_amount, Money), 'down_payment_amount is not a Money class: %r' % down_payment_amount
        assert isinstance(amortization_year, int), 'amortization_year is not a Integer class: %r' % amortization_year
        assert isinstance(annual_interest_rate, Decimal), 'annual_interest_rate is not a Decimal class: %r' % annual_interest_rate
        assert isinstance(payment_frequency, Decimal), 'payment_frequency is not a Decimal class: %r' % payment_frequency
        assert isinstance(compounding_period, Decimal), 'compounding_period is not a Money class: %r' % compounding_period

        # Convert the date input into python "Date" object.
        first_payment_date_obj = None
        if not isinstance(first_payment_date, datetime):
            if not isinstance(first_payment_date, str):
                raise("first_payment_date is not String nor Datetime object.")
            else:
                first_payment_date_obj = datetime.strptime(first_payment_date, "%Y-%m-%d").date()
        else:
            first_payment_date_obj = first_payment_date

        # Save to class member variables.
        self._currency = currency
        self._total_amount = total_amount
        self._down_payment_amount = down_payment_amount
        self._loan_amount = self._total_amount - self._down_payment_amount
        self._amortization_year = amortization_year
        self._annual_interest_rate = annual_interest_rate
        self._payment_frequency = payment_frequency
        self._compounding_period = compounding_period
        self._first_payment_date = first_payment_date_obj

    def get_payment_frequency(self):
        return self._payment_frequency

    def percent_of_loan_financed(self):
        loanPurchaseAmount = self._total_amount
        downPayment = self._down_payment_amount

        if loanPurchaseAmount is 0:  # Defensive Code: Prevent division by zero error.
            return 0

        # Calculate our loan princinple.
        loanAmount = loanPurchaseAmount - downPayment
        amountFinancedPercent = loanAmount.amount / loanPurchaseAmount.amount
        return amountFinancedPercent * 100

    def interest_rate_per_payment_frequency(self):
        compoundingPeriod = self._compounding_period
        annualInterestRate = self._annual_interest_rate
        paymentFrequency = self._payment_frequency

        y = compoundingPeriod / paymentFrequency
        x = annualInterestRate / compoundingPeriod
        x = x + 1

        #WARNING: Precision loss
        z = math.pow(x, y)
        z = z - 1.0;
        return z

    def total_number_of_payments_per_frequency(self):
        amortYear = self._amortization_year
        payment_frequency = self._payment_frequency
        totalPayments = amortYear * payment_frequency
        return totalPayments

    def mortgage_payment_per_payment_frequency(self):
        """
        Function will return the amount paid per payment based on the frequency.
        """
        # Calculate the interest rate per the payment parameters:
        r = self.interest_rate_per_payment_frequency()

        # Calculate the total number of payments given the parameters:
        n = self.total_number_of_payments_per_frequency()

        # Variables used as number holders.
        p = self._loan_amount
        mortgage = None
        top = None
        bottom = None

        top = r + 1
        top = math.pow(top, n)
        top = r * top

        bottom = r + 1
        bottom = math.pow(bottom, n)
        bottom = bottom - 1

        if bottom == 0:
            return 0

        mortgage = (top / bottom)
        mortgage = mortgage * p

        return mortgage

    def mortgage_payment_schedule(self):
        # Initialize the payment schedule which will include all necessary data.
        paymentSchedule = []
        mortgagePayment = self.mortgage_payment_per_payment_frequency()
        interestRatePerPayment = Decimal(self.interest_rate_per_payment_frequency())
        loanBalance = self._loan_amount
        totalPaidToInterest = Money(amount=0, currency=self._currency)
        totalPaidToBank = Money(amount=0, currency=self._currency)
        current_payment_date = self._first_payment_date

        # Go through all the years of the loan.
        for amortizationYear in range(1, self._amortization_year+1):

            # Go through all the payments in that year.
            for payment in range(1, int(self._payment_frequency)+1):

                # Calculate amount going to pay off interest.
                interestAmount = loanBalance * interestRatePerPayment

                # Calculate amount going to pay off principle.
                principleAmount = mortgagePayment - interestAmount

                # Calculate the remaining loan balance.
                loanBalance = loanBalance - principleAmount
                totalPaidToInterest = interestAmount + totalPaidToInterest
                totalPaidToBank = mortgagePayment + totalPaidToBank

                # Calculate the current payment date according to the year/ month/ etc
                # that the computation is currently on.
                if self._payment_frequency is MORTGAGEKIT_ANNUAL:
                    current_payment_date += relativedelta(years=1)
                elif self._payment_frequency is MORTGAGEKIT_SEMI_ANNUAL:
                    current_payment_date += relativedelta(months=6)
                elif self._payment_frequency is MORTGAGEKIT_QUARTER:
                    current_payment_date += relativedelta(months=4)
                elif self._payment_frequency is MORTGAGEKIT_BI_MONTH:
                    current_payment_date += relativedelta(months=2)
                elif self._payment_frequency is MORTGAGEKIT_MONTH:
                    current_payment_date += relativedelta(months=1)
                elif self._payment_frequency is MORTGAGEKIT_BI_WEEK:
                    current_payment_date += relativedelta(weeks=2)
                elif self._payment_frequency is MORTGAGEKIT_WEEK:
                    current_payment_date += relativedelta(weeks=1)

                # Save the computation we've generated.
                paymentSchedule.append({
                    'year': amortizationYear,
                    'interval': payment,
                    'payment': mortgagePayment,
                    'interest': interestAmount,
                    'principle': principleAmount,
                    'loan_balance': loanBalance,
                    'totalPaidToInterest': totalPaidToInterest,
                    'totalPaidToBank': totalPaidToBank,
                    'paymentData': current_payment_date
                })

        return paymentSchedule

    def monthly_mortgage_payment(self):
        """
        Function will return the amount paid per payment standardized to
        a per monthly bases.
        """
        mortgage_payment = self.mortgage_payment_per_payment_frequency()
        frequency = self._payment_frequency
        monthly_mortgage_payment = None

        if frequency == MORTGAGEKIT_ANNUAL:  # Annual
            monthly_mortgage_payment = mortgage_payment / Decimal(MORTGAGEKIT_MONTH)

        elif frequency == MORTGAGEKIT_SEMI_ANNUAL:  # Semi-annual
            monthly_mortgage_payment = mortgage_payment / Decimal(MORTGAGEKIT_BI_MONTH)

        elif frequency == MORTGAGEKIT_QUARTER:  # Quarterly
            monthly_mortgage_payment = mortgage_payment / Decimal(MORTGAGEKIT_QUARTER)

        elif frequency == MORTGAGEKIT_BI_MONTH:
            monthly_mortgage_payment = mortgage_payment / Decimal(MORTGAGEKIT_SEMI_ANNUAL)

        if frequency == MORTGAGEKIT_MONTH:
            monthly_mortgage_payment = mortgage_payment

        elif frequency == MORTGAGEKIT_BI_WEEK:
            monthly_mortgage_payment = mortgage_payment * Decimal(MORTGAGEKIT_BI_WEEK) / Decimal(MORTGAGEKIT_MONTH)

        elif frequency == MORTGAGEKIT_WEEK:
            monthly_mortgage_payment = mortgage_payment * Decimal(MORTGAGEKIT_WEEK) / Decimal(MORTGAGEKIT_MONTH)

        else:
            raise Exception("WARNING: Unsupported payment frequency type!")

        return monthly_mortgage_payment

    def annual_mortgage_payment(self):
        """
        Function will return the amount paid per payment standardized to
        a per annual bases.
        """
        mortgage_payment = self.mortgage_payment_per_payment_frequency()
        frequency = self._payment_frequency
        monthly_mortgage_payment = None

        if frequency == MORTGAGEKIT_ANNUAL:
            monthly_mortgage_payment = mortgage_payment

        elif frequency == MORTGAGEKIT_SEMI_ANNUAL:
            monthly_mortgage_payment = mortgage_payment * Decimal(MORTGAGEKIT_SEMI_ANNUAL)

        elif frequency == MORTGAGEKIT_QUARTER:
            monthly_mortgage_payment = mortgage_payment * Decimal(MORTGAGEKIT_QUARTER)

        elif frequency == MORTGAGEKIT_BI_MONTH:
            monthly_mortgage_payment = mortgage_payment * Decimal(MORTGAGEKIT_BI_MONTH)

        if frequency == MORTGAGEKIT_MONTH:
            monthly_mortgage_payment = mortgage_payment * Decimal(MORTGAGEKIT_MONTH)

        elif frequency == MORTGAGEKIT_BI_WEEK:
            monthly_mortgage_payment = mortgage_payment * Decimal(MORTGAGEKIT_BI_WEEK)

        elif frequency == MORTGAGEKIT_WEEK:
            monthly_mortgage_payment = mortgage_payment * Decimal(MORTGAGEKIT_WEEK)

        else:
            raise Exception("WARNING: Unsupported payment frequency type!")

        return monthly_mortgage_payment
