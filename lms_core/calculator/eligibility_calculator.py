from decimal import *
from ..exceptions.lms_exception import CustomerNotEligible
def is_eligible_for_loan(loan_type, loan_customer, previous_loans):

    """
    Checks if the customer is eligible to apply for a loan and calculates the maximum loan amount they can apply for.
    
    Args:
        loan_customer (LoanCustomer): The customer applying for the loan.
        loan_type (LoanType): The type of loan the customer is applying for.
        previous_loans (QuerySet): All previous loans of the customer.
        
    Returns:
        bool: True if the customer is eligible, False otherwise.
        str: Message explaining eligibility.
        Decimal: The maximum loan amount the customer can apply for (if eligible).
    """

    # Check credit score eligibility
    if loan_customer.credit_score < loan_type.min_credit_score:
        return False, f"Your credit score of {loan_customer.credit_score} does not meet the minimum required score of {loan_type.min_credit_score} for this loan.", Decimal(0)
    
    # Check if the customer has more than 3 loans of the same type
    same_type_loans = previous_loans.filter(application__loan_type=loan_type)
    if same_type_loans.count() > 3:
        return False, "You already have 3 or more loans of this type.", Decimal(0)
    
    # Check if the customer has any overdue loans
    overdue_loans = previous_loans.filter(status='OVERDUE')
    if overdue_loans.exists():
        return False, "You have overdue loans, making you ineligible for a new loan.", Decimal(0)
    
    # Calculate total EMIs for all active loans
    active_loans = previous_loans.filter(status='ACTIVE')
    total_active_emi = sum(loan.emi_amount for loan in active_loans)
    print('total_Active_emi: ',total_active_emi)
    # Define maximum allowable EMI as a percentage of the customer's income (e.g., 50%)
    max_emi_percentage = 0.5
    max_allowed_emi = Decimal(loan_customer.income) * Decimal(max_emi_percentage)
    print('max_allowed_emi: ', max_allowed_emi)
    # Calculate the EMI that would result from the new loan (using a simple formula for equal installments)
    new_loan_interest_rate = loan_type.interest_rate/ 100
    new_loan_term_years = loan_type.max_tenure_years  # Assuming a default loan term of 5 years
    months = new_loan_term_years * 12

    # Calculate max eligible EMI customer can afford for the new loan
    remaining_emi_capacity = max_allowed_emi - total_active_emi
    print('remaining_emi_capacity: ', remaining_emi_capacity)
    # If the customer cannot afford any additional EMI, they are ineligible
    if remaining_emi_capacity <= 0:
        return False, "Your current EMI obligations exceed the allowable limit based on your income.", Decimal(0)

    # Banks often use a loan-to-value (LTV) ratio to determine how much of the property's value can be loaned  
    loan_to_value_ratio=0.8
    # Calculate maximum loan amount customer can apply for based on remaining EMI capacity
    max_loan_amount = ((remaining_emi_capacity * (1 - (1 + new_loan_interest_rate)**-months)) / new_loan_interest_rate) * Decimal(1/loan_to_value_ratio)
    print('max_loan_amount before: ', max_loan_amount)
    #Calculate the max_loan_amount based on the credit_score
    max_loan_amount = max_loan_amount + max_loan_amount *(loan_customer.credit_score - loan_type.min_credit_score)/850
    # Ensure the max loan amount doesn't exceed the max limit for this loan type
    print('max_loan_amount between: ', max_loan_amount)
    max_loan_amount = min(max_loan_amount, loan_type.max_amount)
    print('max_loan_amount after: ', max_loan_amount)
    # Return eligibility and the max loan amount customer can apply for
    return True, "You are eligible for this loan.", max_loan_amount
    

def get_customer_eligibility(loan_type, loan_customer, previous_loans):
    if loan_customer is None or loan_customer.income is None or loan_customer.credit_score is None:
        raise CustomerNotEligible('Missing income and credit score. Please update details')
    is_eligible, msg, max_amount = is_eligible_for_loan(loan_type,loan_customer, previous_loans)
    if is_eligible:
        return max_amount
    else:
        raise CustomerNotEligible(msg)