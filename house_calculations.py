"""
Module: house_calculations.py
----------------------------
Provides the Mortgage class to calculate mortgage payments, generate payment schedules, and visualise loan repayment, equity, and house price forecasts.

Dependencies: numpy, pandas, matplotlib, numpy_financial, mortgage.Loan
Author: MPon
Modified: 2026-04-05
"""

import numpy as np
import pandas as pd
from datetime import date
import numpy_financial as npf
import matplotlib.pyplot as plt

"""
Minimal Loan class for mortgage calculations (standalone version).
"""
class Loan:
    def __init__(self, principal, interest, term):
        self.principal = principal
        self.interest = interest
        self.term = term
        self.summarize = self._summary()

    def _summary(self):
        return f"Loan(principal={self.principal}, interest={self.interest}, term={self.term})"

class Mortgage:
    """
    Mortgage class for calculating mortgage payments, generating payment schedules, and visualising repayment and equity.
    
    Attributes:
        house_price (float): Total price of the house.
        interest_rate (float): Annual interest rate as a decimal.
        mortgage_length (int): Length of the mortgage in years.
        deposit (float): Initial deposit amount.
        mortgage (float): Principal to be borrowed.
        start_date (str): Start date of the mortgage (DD/MM/YYYY).
    """
    def __init__(self, house_price, interest, mortgage_length):
        """
        Initialise a Mortgage instance.
        Args:
            house_price (float): Total price of the house.
            interest (float): Annual interest rate as a percentage (e.g., 3 for 3%).
            mortgage_length (int): Length of the mortgage in years.
        """
        self.house_price = house_price
        today = date.today()
        self.start_date = today.strftime("%d/%m/%Y")
        self.mortgage_length = mortgage_length
        self.interest_rate = interest / 100
        lifetime_isa = 10000  # Lifetime ISA government bonus (GBP)
        right_to_acquire = 10000  # Right to Acquire discount (GBP)
        deposit = lifetime_isa
        self.deposit = deposit
        # Principal to be borrowed
        self.mortgage = house_price - (self.deposit + right_to_acquire)

    @staticmethod
    def other_expenses_calculator(local_authority_searches, drainage_searches, environmental_searches):
        """
        Calculate other one-off expenses related to the house purchase.
        Args:
            local_authority_searches (float): Cost of local authority searches.
            drainage_searches (float): Cost of drainage searches.
            environmental_searches (float): Cost of environmental searches.
        Returns:
            float: Total other expenses.
        """
        other_expenses = 0
        other_expenses += local_authority_searches + drainage_searches + environmental_searches
        return other_expenses
    # Example usage (not recommended in class body):
    # other_expenses_calculator(125, 30, 35)

    def mortgage_Calculator(self):
        """
        Calculate the monthly payment using the external Loan class.
        Returns:
            Loan: Loan object with payment summary.
        """
        monthly_payment = Loan(principal=self.mortgage, interest=self.interest_rate, term=self.mortgage_length)
        print(monthly_payment.summarize)
        return monthly_payment

    def mortgage_Calculator_2(self):
        """
        Calculate the monthly payment using numpy_financial.pmt formula.
        Returns:
            float: Monthly payment amount (GBP).
        """
        monthly_payment_2 = float(
            "{0:.2f}".format(-1 * npf.pmt(self.interest_rate / 12, self.mortgage_length * 12, self.mortgage)))
        # Total mortgage paid over the term (not used)
        mortgage_total = float("{0:.2f}".format(12 * monthly_payment_2 * self.mortgage_length))
        return monthly_payment_2

    def mortgage_Calculator_3(self):
        """
        Calculate the monthly payment using the standard amortisation formula.
        Returns:
            float: Monthly payment amount (GBP).
        """
        npr = self.mortgage_length * 12
        interest_rate_2 = self.interest_rate / 12
        numerator = interest_rate_2 * ((1 + interest_rate_2) ** npr)
        denominator = (1 + interest_rate_2) ** npr - 1
        monthly_payment = float("{0:.2f}".format(self.mortgage * numerator / denominator))
        return monthly_payment

    def mortgage_Calculator_4(self):
        """
        Calculate monthly payment using an alternative formula (equivalent to mortgage_Calculator_3).
        Returns:
            float: Monthly payment amount (GBP).
        """
        monthly_payment = float(
            "{0:.2f}".format(self.mortgage * ((self.interest_rate / 12) * ((1 + (self.interest_rate / 12)) ** (
                    self.mortgage_length * 12))) / (
                                     (1 + (self.interest_rate / 12)) ** (self.mortgage_length * 12) - 1)))
        return monthly_payment

    def create_DataFrame(self, return_df=False):
        """
        Create a DataFrame representing the mortgage payment schedule.
        Columns: Payment, Principal Paid, Interest Paid, Balance.
        Also triggers plotting of repayment, equity, and forecast diagrams unless return_df is True.
        Args:
            return_df (bool): If True, only return the DataFrame and do not plot.
        Returns:
            pd.DataFrame: Payment schedule DataFrame (if return_df is True).
        """
        passed_monthly_payment = self.mortgage_Calculator_2()
        payment_date = pd.date_range(self.start_date, periods=self.mortgage_length * 12, freq="MS")
        payment_date.name = "Payment Date"
        df = pd.DataFrame(index=payment_date, columns=["Payment", "Principal Paid", "Interest Paid", "Balance"],
                          dtype='float')
        df.reset_index(inplace=True)
        df.index += 1
        df.index.name = "Month"
        df["Payment"] = passed_monthly_payment
        # Calculate principal and interest paid for each month
        df["Principal Paid"] = -1 * npf.ppmt(self.interest_rate / 12, df.index, self.mortgage_length * 12,
                                             self.mortgage)
        df["Interest Paid"] = -1 * npf.ipmt(self.interest_rate / 12, df.index, self.mortgage_length * 12, self.mortgage)
        df = df.round(2)
        # Ensure 'Balance' column is a float to avoid assignment errors
        df["Balance"] = df["Balance"].astype(float)
        # Set initial balance after first payment
        df.loc[1, "Balance"] = self.mortgage - df.loc[1, "Principal Paid"]
        for months in range(2, len(df) + 1):
            previous_balance = df.loc[months - 1, "Balance"]
            principal_paid = df.loc[months, "Principal Paid"]
            if previous_balance == 0:
                # If loan is paid off, set all remaining values to zero
                df.loc[months, ["Payment", "Principal Paid", "Interest Paid", "Balance"]] == 0
                continue
            elif principal_paid <= previous_balance:
                df.loc[months, "Balance"] = previous_balance - principal_paid
        if return_df:
            return df
        print(df)
        self.create_Loan_Repayment_Diagram(df)
        self.create_House_Equity_Diagram(df)
        self.create_Forecast_House_Price_Diagram(df)

    @staticmethod
    def create_Loan_Repayment_Diagram(df, return_fig=False):
        """
        Plot the loan repayment plan, showing principal and interest paid over time.
        Args:
            df (pd.DataFrame): Payment schedule DataFrame.
            return_fig (bool): If True, return the matplotlib Figure object instead of showing.
        Returns:
            matplotlib.figure.Figure or None
        """
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        ax.set_title("Loan Repayment Plan", fontsize=12)
        # Y axis doesn't look right (possible scaling issue)
        ax.plot(df.index, df["Principal Paid"], color="blue", label="Principal")
        ax.plot(df.index, df["Interest Paid"], color="red", label="Interest")
        ax.set_xlabel("Months", fontsize=12)
        ax.set_ylabel("Amount (£)", fontsize=12)
        ax.legend(loc=0)
        ax.set_ylim(bottom=0)
        ax.set_xlim(left=0)
        ax.grid(True)
        if return_fig:
            return fig
        plt.show()

    @staticmethod
    def create_House_Equity_Diagram(df, return_fig=False):
        """
        Plot the cumulative house equity and interest paid over time.
        Args:
            df (pd.DataFrame): Payment schedule DataFrame.
            return_fig (bool): If True, return the matplotlib Figure object instead of showing.
        Returns:
            matplotlib.figure.Figure or None
        """
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        ax.set_title("House Equity", fontsize=12)
        cumulative_home_equity = np.cumsum(df["Principal Paid"])
        cumulative_interest_paid = np.cumsum(df["Interest Paid"])
        ax.plot(df.index, cumulative_home_equity, color="blue", label="Principal")
        ax.plot(df.index, cumulative_interest_paid, color="red", label="Interest")
        ax.set_xlabel("Months", fontsize=12)
        ax.set_ylabel("Amount (£)", fontsize=12)
        ax.legend(loc=0)
        ax.set_ylim(bottom=0)
        ax.set_xlim(left=0)
        ax.grid(True)
        if return_fig:
            return fig
        plt.show()

    def create_Forecast_House_Price_Diagram(self, df):
        """
        Plot the forecasted house price and equity over time, assuming a constant growth rate.
        Args:
            df (pd.DataFrame): Payment schedule DataFrame.
        """
        n_months = len(df)
        plt.figure(figsize=(10, 5), dpi=50)
        plt.title("Forecast House Price", fontsize=12)
        growth_rate_year_min = 3.5  # not used, placeholder for min scenario
        growth_rate_year_max = 3.8  # not used, placeholder for max scenario
        growth_rate_year = 3.5  # Assumed annual house price growth rate (%)
        growth_rate_month = (growth_rate_year / 12) / 100
        cumulative_house_equity = np.cumsum(df["Principal Paid"])
        growth_array = np.full(n_months, growth_rate_month)
        forecast_growth = np.cumprod(1 + growth_array)
        forecast_house_value = self.house_price * forecast_growth
        # Calculate percent owned: deposit plus principal paid as a fraction of house price
        cumulative_percent_owned = (self.deposit / 100) + (cumulative_house_equity / self.house_price)
        forecast_house_equity = cumulative_percent_owned * forecast_house_value
        plt.plot(df.index, forecast_house_value, color="green", label="House Value")
        plt.plot(df.index, forecast_house_equity, color="purple", label="House Equity")
        plt.xlabel("Months", fontsize=12)
        plt.ylabel("Amount (£)", fontsize=12)
        plt.legend(loc=0)
        plt.ylim(ymin=0)
        plt.xlim(xmin=0)
        plt.grid(True)
        plt.show()  # mpld3.show()


# Example usage
if __name__ == "__main__":
    m = Mortgage(house_price=150000, interest=3, mortgage_length=30)
    m.mortgage_Calculator()
    m.create_DataFrame()
