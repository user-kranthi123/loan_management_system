import math
from ..exceptions.lms_exception import LoanException
from decimal import *
def calculate_emi(loan_application):
    """
        To calculate the EMI (Equated Monthly Installment) for a loan, we need to consider the loan amount, interest rate, and loan tenure (in months). The formula to calculate EMI is:
            EMI=P⋅r⋅(1+r)**n/(1+r)**n−1

        Where:
            PP = Loan amount (principal)
            r = Monthly interest rate (annual interest rate / 12 / 100)
            n = Loan tenure (number of months)
        Args:
            loan_application (LoanApplication): The loan_application of the customer
        Returns:
            calculated emi
    """
    principal = loan_application.loan_amount
    interest_rate = loan_application.loan_type.interest_rate
    loan_term_months = loan_application.loan_type.max_tenure_years*12
    monthly_interest_rate = interest_rate /12/100
    if monthly_interest_rate == 0:
        emi_amount = principal / loan_term_months
    else:
        emi_amount = principal * monthly_interest_rate * Decimal(math.pow((1 + monthly_interest_rate), loan_term_months)) / Decimal((math.pow((1 + monthly_interest_rate), loan_term_months) - 1))
    print('calculated_emi:', emi_amount)
    return round(emi_amount, 2)