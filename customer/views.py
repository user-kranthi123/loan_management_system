from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
import requests
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib import messages
from lms_core.exceptions.lms_exception import UserException, DocumentException
from lms_core.calculator.eligibility_calculator import get_customer_eligibility
from lms_core.exceptions.lms_exception import CustomerNotEligible, LoanException, PaymentException
from lms_core.validator.payment_validator import check_emi_payment
from lms_core.calculator.emi_calculator import calculate_emi
import os
from . import forms as CFORM
from . import models as CMODEL
from lms import models as LMODEL
from lms import forms as LFORM
from decimal import *
from datetime import datetime

DOCUMENT_API_GATEWAY = ""

def login_view(request):
    """
    This function handles user login by displaying a form, authenticating user credentials upon form submission, and logging in the user if credentials are valid. 
    If authentication fails, it displays an error message. It renders the login page on GET requests or after failed attempts.
    """
    form = CFORM.UserForm()
    data = {'form':form}
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password1')
             # Authenticates the user by checking if the provided credentials are valid
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successfully!")
                return redirect('/postlogin')
            else:
                # If authentication fails, display an error message
                messages.error(request, 'Invalid username or password.')
        except Exception as e:
            print('user login failed: ', e)
            messages.error(request, 'unable to login')
    return render(request, 'home/login.html', context = data)

def signup_page_view(request):
    """
    This function handles user sign-up by displaying forms for both user and customer details. 
    Upon form submission, it validates the data, uploads a profile picture to S3, and creates user and customer records. 
    If successful, the user is added to the 'LMS_USER' group and redirected to the login page; otherwise, error messages are shown.
    """
    if request.user.is_authenticated:
        return HttpResponseRedirect('/postlogin')
    # Initialize empty forms for user and customer information
    user_form = CFORM.UserForm()
    customer_form = CFORM.CustomerForm()
    if request.method == 'POST':
        try:
            user_form= CFORM.UserForm(request.POST)
            customer_form = CFORM.CustomerForm(request.POST)
            print('customerForm: ', customer_form)
            if user_form.is_valid() and customer_form.is_valid():
                user = user_form.save(commit=False)
                customer =  customer_form.save(commit=False)
                profile_pic  = request.FILES["profile_pic"]
                # Generate a signed token for document upload using lambda function
                # response = get_signed_token(request)
                # if(response['status']=='SUCCESS') :
                    #upload the profile_pic to s3 storage and save the url_path
                    # print('upload document respone: ', upload_doc_to_s3(response['data'], profile_pic))
                # customer.s3_document_url = f"{response['data']['url']}{response['data']['fields']['key']}"
                user.save()
                customer.user = user
                customer.save()
                LMODEL.LoanCustomer.objects.get_or_create(customer=customer)
                # Add the customer to LMS_USER group
                customer_group = Group.objects.get_or_create(name='LMS_USER')
                customer_group[0].user_set.add(user)
                messages.success(request, "user created successfully!")
                return HttpResponseRedirect('/customer/login')
            else:
                messages.error(request, user_form.errors)
                messages.error(request, customer_form.errors)
        # Handle specific custom exceptions for user,document related issues
        except UserException as e:
            print('signup exception: ',e)
            messages.error(request, str(e))
        except DocumentException as e:
            print('Document Upload exception: ', e)
            messages.error(request, 'Unable to save profile_pic')
        except Exception as e:
            print('signup exception: ',e)
            messages.error(request, 'unable to create signup')

    data = {'userForm': user_form, 'customerForm':customer_form}
    return render(request,'home/signup.html', data)

def dashboard_view(request):
    data= {}
    customer = CMODEL.Customer.objects.get(user=request.user)
    data['customer'] =customer
    loan_customer = LMODEL.LoanCustomer.objects.get(customer=customer)
    applications = LMODEL.LoanApplication.objects.filter(customer=loan_customer)
    loans = LMODEL.Loan.objects.filter(application__customer=loan_customer)
    active_loans = 0
    pending_applications = 0
    total_amount = 0
    pending_amount = 0
    for loan in loans:
        if loan.status=='ACTIVE':
            active_loans+=1
            total_amount+=loan.total_amount
            pending_amount+=loan.remaining_balance
    for app in applications:
        if app.status == 'PENDING':
            pending_applications+=1
    data['transactions'] = LMODEL.EMI.objects.filter(loan__in=loans)
    data['loan_customer'] = loan_customer
    data['applications'] = applications
    data['loans'] = loans
    metrics = {'active_loans': active_loans, 
               'pending_amount': pending_amount, 
               'total_amount':total_amount,
               'pending_applications' : pending_applications}
    data['metrics'] = metrics
    print('data for dashboard: ', data)
    return render(request, 'customer/dashboard.html', context= data)

def apply_for_loan(request):
    data = {}
    form = LFORM.LoanApplicationForm()
    try:
        customer = CMODEL.Customer.objects.get(user=request.user)
        loan_customer = LMODEL.LoanCustomer.objects.get(customer = customer)
        previous_loans = LMODEL.Loan.objects.filter(application__customer=loan_customer)
        data['customer'] = customer
        data['loan_customer'] = loan_customer
        if request.method == 'POST':
            form = LFORM.LoanApplicationForm(request.POST, request.FILES)
            if form.is_valid():
                loan_application = form.save(commit=False)
                loan_application.customer = loan_customer
                loan_type=loan_application.loan_type
                loan_amount = get_customer_eligibility(loan_type,loan_customer, previous_loans)
                loan_amount = format(loan_amount, ".2f")
                new_loan_amount = Decimal(loan_application.loan_amount)
                if(Decimal(loan_amount) < new_loan_amount):
                    raise LoanException(f"Amount {new_loan_amount} is greater than eligibility {loan_amount}")
                loan_application.loan_amount = new_loan_amount
                # Handle uploaded documents and generate document URLs
                files = request.FILES['documents']
                # response = get_signed_token(request)
                # if(response['status']=='SUCCESS') :
                    #upload the documents to s3 storage and save the url_path
                    # print('upload document respone: ', upload_doc_to_s3(response['data'], files))
                # loan_application.s3_document_url = f"{response['data']['url']}{response['data']['fields']['key']}"
                loan_application.save()
                print('loan_application: ',loan_application)
                calculated_emi = calculate_emi(loan_application)
                LMODEL.Loan(application=loan_application,loan_term_months=loan_type.max_tenure_years*12, total_amount=new_loan_amount, remaining_balance=new_loan_amount, emi_amount=Decimal(calculated_emi), status='PENDING').save()
                messages.success(request, "Loan application submitted successfully!")
                return HttpResponseRedirect('/customer/dashboard')
    except LoanException as e:
        messages.error(request, str(e))
    except CustomerNotEligible as e:
        messages.error(request,str(e))
    except Exception as e:
        print('apply loan exp: ', e)
        messages.error(request, "unable to apply for loan")
    data['form'] = form
    return render(request, 'lms/apply_for_loan.html', context=data)

def pay_emi_view(request, pk):
    data = {}
    try:
        customer = CMODEL.Customer.objects.get(user= request.user)
        loan_customer = LMODEL.LoanCustomer.objects.get(customer = customer)
        data['customer'] = customer
        data['loan_customer'] = loan_customer
        loan = LMODEL.Loan.objects.get(id=pk)
        data['loan'] = loan
        if request.method == 'POST':
            form = LFORM.EMIPaymentForm(request.POST)
            emi = form.save(commit=False)
            if form.is_valid():
                emi = form.save(commit=False)
                emi.loan = loan
                check_emi_payment(emi, loan)
                loan.remaining_balance=loan.remaining_balance-emi.amount_paid
                emi.remaining_balance_after_payment = loan.remaining_balance
                emi.save()
                loan.save()
                messages.success(request, "EMI payment successfully!")
                return HttpResponseRedirect('/customer/dashboard')
    except PaymentException as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, "unable to make payment")
    data['form'] = LFORM.EMIPaymentForm()
    return render(request, 'lms/emi_transaction.html', context= data)


def upload_doc_to_s3(data, file):
    files = {'file':file.read()}
    response = requests.post(data['url'], data = data['fields'],files= files)
    if response.status_code == 200 or response.status_code== 204:
        return 'Image Uploaded successfully'
    else:
        raise DocumentException("Unable to upload documents to s3")
    pass

def get_signed_token(request):
    response = requests.post(DOCUMENT_API_GATEWAY)
    if response.status_code == 200:
        return response.json()
    else:
        raise DocumentException("Unable to upload documents to s3")


def update_loan_customer(request):
    data = {}
    # Assuming the logged-in customer is linked with a LoanCustomer instance
    customer = CMODEL.Customer.objects.get(user= request.user)
    loan_customer, created = LMODEL.LoanCustomer.objects.get_or_create(customer=customer)
    
    if request.method == 'POST':
        form = LFORM.LoanCustomerForm(request.POST, instance=loan_customer)
        print('LoanCustomerForm: ', form)
        if form.is_valid():
            form.save()
            messages.success(request, "Details updated successfully")
            return HttpResponseRedirect('/customer/dashboard')
        else:
            print('Errors: ', form.errors)
            messages.error(request, form.errors)
    form = LFORM.LoanCustomerForm(instance=loan_customer)
    data['form']= form
    data['customer'] = customer
    data['loan_customer'] = loan_customer
    return render(request, 'customer/update-customer.html', context=data)