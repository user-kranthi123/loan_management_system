from ..exceptions.lms_exception import  PaymentException
def is_emi_valid(emi, loan):
    if emi is None  or loan is None:
        return False, "EMI or loan is invalid!"
    if emi.amount_paid <=0:
        return False, "Amount paid should be greater than 0."
    if emi.amount_paid < loan.emi_amount:
        return False, f"EMI Amount is less than min emi_amount {loan.emi_amount}"
    if emi.amount_paid > loan.remaining_balance:
        return False, f"EMI Amount exceeds loan remaining balance {loan.remaining_balance}"
    return True, "EMI Payment is valid"

def check_emi_payment(emi, loan):
    valid, message = is_emi_valid(emi, loan)
    if valid:
        return valid
    else:
        raise PaymentException(message)