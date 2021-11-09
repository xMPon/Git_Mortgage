import mpld3
import numpy as np
import pandas as pd
from datetime import date
from mortgage import Loan
import numpy_financial as npf
import matplotlib.pyplot as plt


class Mortgage:
    def __init__(self, house_price, interest, mortgage_length):
        self.house_price = house_price
        today = date.today()
        self.start_date = today.strftime("%d/%m/%Y")
        self.mortgage_length = mortgage_length
        self.interest_rate = interest / 100
        lifetime_isa = 10000
        right_to_acquire = 10000
        deposit = lifetime_isa
        self.deposit = deposit
        self.mortgage = house_price - (self.deposit + right_to_acquire)

    def other_expenses_calculator(local_authority_searches, drainage_searches, environmental_searches):
        other_expenses = 0
        other_expenses += local_authority_searches + drainage_searches + environmental_searches
        return other_expenses
    other_expenses_calculator(125, 30, 35)

    def mortgage_Calculator(self):
        monthly_payment = Loan(principal=self.mortgage, interest=self.interest_rate, term=self.mortgage_length)
        print(monthly_payment.summarize)
        return monthly_payment
    def mortgage_Calculator_2(self):
        monthly_payment_2 = float(
            "{0:.2f}".format(-1 * npf.pmt(self.interest_rate / 12, self.mortgage_length * 12, self.mortgage)))
        mortgage_total = float("{0:.2f}".format(12 * monthly_payment_2 * self.mortgage_length))
        return monthly_payment_2
    def mortgage_Calculator_3(self):
        npr = self.mortgage_length * 12
        interest_rate_2 = self.interest_rate / 12
        numerator = interest_rate_2 * ((1 + interest_rate_2) ** npr)
        denominator = (1 + interest_rate_2) ** npr - 1
        monthly_payment = float("{0:.2f}".format(self.mortgage * numerator / denominator))
        return monthly_payment
    def mortgage_Calculator_4(self):
        monthly_payment = float(
            "{0:.2f}".format(self.mortgage * ((self.interest_rate / 12) * ((1 + (self.interest_rate / 12)) ** (
                    self.mortgage_length * 12))) / (
                                     (1 + (self.interest_rate / 12)) ** (self.mortgage_length * 12) - 1)))
        return monthly_payment

    def create_DataFrame(self):
        passed_monthly_payment = self.mortgage_Calculator_2()
        payment_date = pd.date_range(self.start_date, periods=self.mortgage_length * 12, freq="MS")
        payment_date.name = "Payment Date"
        df = pd.DataFrame(index=payment_date, columns=["Payment", "Principal Paid", "Interest Paid", "Balance"],
                          dtype='float')
        df.reset_index(inplace=True)
        df.index += 1
        df.index.name = "Month"
        df["Payment"] = passed_monthly_payment
        df["Principal Paid"] = -1 * npf.ppmt(self.interest_rate / 12, df.index, self.mortgage_length * 12,
                                             self.mortgage)
        df["Interest Paid"] = -1 * npf.ipmt(self.interest_rate / 12, df.index, self.mortgage_length * 12, self.mortgage)
        df = df.round(2)
        df["Balance"] = 0
        df.loc[1, "Balance"] = self.mortgage - df.loc[1, "Principal Paid"]
        for months in range(2, len(df) + 1):
            previous_balance = df.loc[months - 1, "Balance"]
            principal_paid = df.loc[months, "Principal Paid"]
            if previous_balance == 0:
                df.loc[months, ["Payment", "Principal Paid", "Interest Paid", "Balance"]] == 0
                continue
            elif principal_paid <= previous_balance:
                df.loc[months, "Balance"] = previous_balance - principal_paid
        print(df)
        self.create_Loan_Repayment_Diagram(df)
        self.create_House_Equity_Diagram(df)
        self.create_Forecast_House_Price_Diagram(df)

    @staticmethod
    def create_Loan_Repayment_Diagram(df):
        plt.figure(figsize=(10, 5), dpi=100)
        plt.title("Loan Repayment Plan", fontsize=12)
        # Y axis doesn't look right
        plt.plot(df.index, df["Principal Paid"], color="blue", label="Principal")
        plt.plot(df.index, df["Interest Paid"], color="red", label="Interest")
        plt.xlabel("Months", fontsize=12)
        plt.ylabel("Amount (£)", fontsize=12)
        plt.legend(loc=0)
        plt.ylim(ymin=0)
        plt.xlim(xmin=0)
        plt.grid(True)
        plt.show()

    @staticmethod
    def create_House_Equity_Diagram(df):
        plt.figure(figsize=(10, 5), dpi=100)
        plt.title("House Equity", fontsize=12)
        cumulative_home_equity = np.cumsum(df["Principal Paid"])
        cumulative_interest_paid = np.cumsum(df["Interest Paid"])
        plt.plot(df.index, cumulative_home_equity, color="blue", label="Principal")
        plt.plot(df.index, cumulative_interest_paid, color="red", label="Interest")
        plt.xlabel("Months", fontsize=12)
        plt.ylabel("Amount (£)", fontsize=12)
        plt.legend(loc=0)
        plt.ylim(ymin=0)
        plt.xlim(xmin=0)
        plt.grid(True)
        plt.show()

    def create_Forecast_House_Price_Diagram(self, df):
        passed_monthly_payment = int(self.mortgage_Calculator_2())
        plt.figure(figsize=(10, 5), dpi=50)
        plt.title("Forecast House Price", fontsize=12)
        growth_rate_year_min = 3.5  # not used
        growth_rate_year_max = 3.8  # not used
        growth_rate_year = 3.5
        growth_rate_month = (growth_rate_year / 12) / 100
        cumulative_house_equity = np.cumsum(df["Principal Paid"])
        growth_array = np.full(passed_monthly_payment, growth_rate_month)
        forecast_growth = np.cumprod(1 + growth_array)
        forecast_house_value = self.house_price * forecast_growth
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


m = Mortgage(house_price=150000, interest=3, mortgage_length=30)
m.mortgage_Calculator()
m.create_DataFrame()
