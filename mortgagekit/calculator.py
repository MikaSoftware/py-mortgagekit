# -*- coding: utf-8 -*-
"""
API library for mortgage calculations.
See README for more details.
"""

from __future__ import print_function
import sys
import argparse
from datetime import datetime, timedelta
import decimal
import math
from dateutil.relativedelta import relativedelta
from moneyed import Money, USD
from moneyed.localization import format_money


__author__ = "Bartlomiej Mika"
__copyright__ = "Copyright (c) 2017, Mika Software Corporation"
__credits__ = ["Bartlomiej Mika", "David Stubbs"]
__license__ = "BSD 2-Clause License"
__version__ = "1.0.0"
__maintainer__ = "Mika Software Corporation"
__email = "bart@mikasoftware.com"
__status__ = "Production"


MORTGAGEKIT_ANNUAL = 1
MORTGAGEKIT_SEMI_ANNUAL = 2
MORTGAGEKIT_QUARTER = 4
MORTGAGEKIT_BI_MONTH = 6
MORTGAGEKIT_MONTH = 12
MORTGAGEKIT_BI_WEEK = 26
MORTGAGEKIT_WEEK = 52


class MortgageCalculator(object):
    """
    Class used to calculate mortgage payments schedule.
    """
    def __init__(self, total_amount, down_payment_amount, amortization_year,
                 annual_interest_rate, payment_frequency, compounding_period,
                 first_payment_date, currency='USD'):
        self._currency = currency
        self._total_amount = Money(amount=total_amount, currency=currency)
        self._down_payment_amount = Money(amount=down_payment_amount, currency=currency)
        self._loan_amount = self._total_amount - self._down_payment_amount
        self._amortization_year = int(amortization_year)
        self._annual_interest_rate = decimal.Decimal(annual_interest_rate)
        self._payment_frequency = int(payment_frequency)
        self._compounding_period = int(compounding_period)
        self._first_payment_date = datetime.strptime(first_payment_date, "%Y-%m-%d").date()

    def get_payment_frequency(self):
        return self._payment_frequency

    def percent_of_loan_financed(self):
        loanPurchaseAmount = self._total_amount
        downPayment = self._down_payment_amount

        if loanPurchaseAmount is 0:  # Defensive Code: Prevent division by zero error.
            return 0

        # Calculate our loan princinple.
        loanAmount = loanPurchaseAmount - downPayment
        amountFinancedPercent = loanAmount / loanPurchaseAmount
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
        interestRatePerPayment = decimal.Decimal(self.interest_rate_per_payment_frequency())
        loanBalance = self._loan_amount
        totalPaidToInterest = Money(amount=0, currency=self._currency)
        totalPaidToBank = Money(amount=0, currency=self._currency)
        current_payment_date = self._first_payment_date

        # Go through all the years of the loan.
        for amortizationYear in range(1, self._amortization_year+1):

            # Go through all the payments in that year.
            for payment in range(1, self._payment_frequency+1):

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
            monthly_mortgage_payment = mortgage_payment / decimal.Decimal(MORTGAGEKIT_MONTH)

        elif frequency == MORTGAGEKIT_SEMI_ANNUAL:  # Semi-annual
            monthly_mortgage_payment = mortgage_payment / decimal.Decimal(MORTGAGEKIT_BI_MONTH)

        elif frequency == MORTGAGEKIT_QUARTER:  # Quarterly
            monthly_mortgage_payment = mortgage_payment / decimal.Decimal(MORTGAGEKIT_QUARTER)

        elif frequency == MORTGAGEKIT_BI_MONTH:
            monthly_mortgage_payment = mortgage_payment / decimal.Decimal(MORTGAGEKIT_SEMI_ANNUAL)

        if frequency == MORTGAGEKIT_MONTH:
            monthly_mortgage_payment = mortgage_payment

        elif frequency == MORTGAGEKIT_BI_WEEK:
            monthly_mortgage_payment = mortgage_payment * decimal.Decimal(MORTGAGEKIT_BI_WEEK) / decimal.Decimal(MORTGAGEKIT_MONTH)

        elif frequency == MORTGAGEKIT_WEEK:
            monthly_mortgage_payment = mortgage_payment * decimal.Decimal(MORTGAGEKIT_WEEK) / decimal.Decimal(MORTGAGEKIT_MONTH)

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
            monthly_mortgage_payment = mortgage_payment * decimal.Decimal(MORTGAGEKIT_SEMI_ANNUAL)

        elif frequency == MORTGAGEKIT_QUARTER:
            monthly_mortgage_payment = mortgage_payment * decimal.Decimal(MORTGAGEKIT_QUARTER)

        elif frequency == MORTGAGEKIT_BI_MONTH:
            monthly_mortgage_payment = mortgage_payment * decimal.Decimal(MORTGAGEKIT_BI_MONTH)

        if frequency == MORTGAGEKIT_MONTH:
            monthly_mortgage_payment = mortgage_payment * decimal.Decimal(MORTGAGEKIT_MONTH)

        elif frequency == MORTGAGEKIT_BI_WEEK:
            monthly_mortgage_payment = mortgage_payment * decimal.Decimal(MORTGAGEKIT_BI_WEEK)

        elif frequency == MORTGAGEKIT_WEEK:
            monthly_mortgage_payment = mortgage_payment * decimal.Decimal(MORTGAGEKIT_WEEK)

        else:
            raise Exception("WARNING: Unsupported payment frequency type!")

        return monthly_mortgage_payment


def main():
    """
    @Precondition:
        Parameters must be of the following.
        - Loan Amount
        - Loan Purchase Amount
        - Down Payment
        - Annual Interest Rate
        - Amortization Years
        - Payment Frequency
        - Compounding Period
        - First Payment Date

    @Postcondition:
        Will return perform the compuation and return the results dictonary.
    """
    parser = argparse.ArgumentParser(description='Mortgage Amortization Calculator')
    parser.add_argument('-t', '--total', default=250000, dest='total_amount')
    parser.add_argument('-dp', '--down-payment', default=50000, dest='down_payment_amount')
    parser.add_argument('-y', '--years', default=25, dest='amortization_year')
    parser.add_argument('-i', '--annual-interest-rate', default=0.04, dest='annual_interest_rate')
    parser.add_argument('-f', '--payment-frequency', default=12, dest='payment_frequency')
    parser.add_argument('-p', '--compounding-period', default=2, dest='compounding_period')
    parser.add_argument('-date', '--first-payment-date', default="2008-01-01", dest='first_payment_date')
    args = parser.parse_args()

    calc = MortgageCalculator(
        args.total_amount,
        args.down_payment_amount,
        args.amortization_year,
        args.annual_interest_rate,
        args.payment_frequency,
        args.compounding_period,
        args.first_payment_date
    )

    payment_schedule = calc.mortgage_payment_schedule()
    print(payment_schedule)

if __name__ == '__main__':
    main()
