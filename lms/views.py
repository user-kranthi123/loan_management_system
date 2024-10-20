from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from . import models as LMODEL
from customer import models as CMODEL
from datetime import date
from decimal import *
from lms_core.calculator.eligibility_calculator import get_customer_eligibility
from lms_core.exceptions.lms_exception import CustomerNotEligible

def home_view(request):
    return render(request, 'home/base.html')

def post_login_view(request):
    if is_customer(request.user):
        return redirect('customer/dashboard')
    return redirect('/admin/')

def is_customer(user):
    return user.groups.filter(name='LMS_USER').exists()

def view_all_loan_types(request):
    loanTypes = LMODEL.LoanType.objects.all()
    data = {'loan_types': loanTypes}
    return render(request, 'lms/all_loan_types.html',context=data)

def check_loan_eligibility(request, pk):
    loan_type = LMODEL.LoanType.objects.get(id=pk)
    customer = CMODEL.Customer.objects.get(user=request.user)
    loan_customer = LMODEL.LoanCustomer.objects.get(customer = customer)
    prev_loans = LMODEL.Loan.objects.filter(application__customer=loan_customer)
    data = {'status':'SUCCESS'}
    try:
        max_loan_amount = Decimal(get_customer_eligibility(loan_type, loan_customer, prev_loans))
        print('max_amount_allowed: ', max_loan_amount)
        data['max_loan_amount'] = format(max_loan_amount, '.2f')
    except CustomerNotEligible as e:
        # messages.error(request, str(e))
        data['status']='FAILURE'
        data['message']=str(e)
    return JsonResponse(data)

def load_sample_data(request):
    print('loading sample data')
    loan_types = [
        LMODEL.LoanType(name="Vehicle Loan", max_amount=Decimal(500000), interest_rate=Decimal(7.5), min_credit_score=750, max_tenure_years=10,description="Loans for purchasing new or used vehicles at competitive rates."),
        LMODEL.LoanType(name="Housing Loan", max_amount=Decimal(2500000), interest_rate=Decimal(8.0), min_credit_score=800, max_tenure_years=20,description="Loans for purchasing your dream home with flexible EMI options."),
        LMODEL.LoanType(name="Personal Loan", max_amount=Decimal(300000), interest_rate=Decimal(10.0), min_credit_score=700, description="Personal loans for education, travel, and other needs."),
    ]

    for loan_type in loan_types:
        loan_type.save()

    customers = CMODEL.Customer.objects.all()

    loan_customers = [
        LMODEL.LoanCustomer(customer=customers[0], income=Decimal(75000), credit_score=750),  # Customer 1
        # LMODEL.LoanCustomer(customer=customers[1], income=Decimal(50000), credit_score=680),  # Customer 2
        # LMODEL.LoanCustomer(customer=customers[2], income=Decimal(120000), credit_score=750), # Customer 3
    ]

    for loan_customer in loan_customers:
        loan_customer.save()
    loan_applications = [
    LMODEL.LoanApplication(customer=loan_customers[0], loan_type=loan_types[0], loan_amount=Decimal(300000), status="PENDING"),
    LMODEL.LoanApplication(customer=loan_customers[0], loan_type=loan_types[1], loan_amount=Decimal(1500000), status="APPROVED",notes="All documents verified and approved"),
    LMODEL.LoanApplication(customer=loan_customers[0], loan_type=loan_types[2], loan_amount=Decimal(400000), status="REJECTED", notes="Documents not valid"),
    ]

    for loan_application in loan_applications:
        loan_application.save()

    loans = [
    LMODEL.Loan(application=loan_applications[0], start_date=date(2023, 1, 15), loan_term_months=120, total_amount=Decimal(300000), remaining_balance=Decimal(300000), emi_amount=Decimal(5000), status='PENDING'),
    LMODEL.Loan(application=loan_applications[1], start_date=date(2023, 5, 10), loan_term_months=240, total_amount=Decimal(1500000), remaining_balance=Decimal(1300000), emi_amount=Decimal(9000), status='ACTIVE'),
    LMODEL.Loan(application=loan_applications[2], start_date=date(2023, 8, 1), loan_term_months=60, total_amount=Decimal(390001), remaining_balance=Decimal(390001), emi_amount=Decimal(7500), status='CLOSED'),
    ]

    for loan in loans:
        loan.save()

    emis = [
    LMODEL.EMI(loan=loans[1], payment_date=date(2023, 2, 15), amount_paid=Decimal(9000), remaining_balance_after_payment=Decimal(1491000)),
    LMODEL.EMI(loan=loans[1], payment_date=date(2023, 3, 15), amount_paid=Decimal(9000), remaining_balance_after_payment=Decimal(1482000)),
    
    LMODEL.EMI(loan=loans[1], payment_date=date(2023, 6, 10), amount_paid=Decimal(100000), remaining_balance_after_payment=Decimal(1382000)),
    LMODEL.EMI(loan=loans[1], payment_date=date(2023, 7, 10), amount_paid=Decimal(82000), remaining_balance_after_payment=Decimal(1300000)),
]

    for emi in emis:
        emi.save()
    print('data loaded successfully')