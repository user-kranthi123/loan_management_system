from django import forms
from .models import LoanApplication, LoanCustomer, EMI
from django.forms.widgets import ClearableFileInput

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ['loan_type', 'loan_amount','documents']
        widgets = {
            'loan_type': forms.Select(attrs={'class': 'form-select'}),
            'loan_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter loan amount'}),
            'documents': ClearableFileInput(attrs={'multiple': False, 'required':False}),
        }

    def __init__(self, *args, **kwargs):
        customer = kwargs.pop('customer', None)  # Passing the customer from the view
        super().__init__(*args, **kwargs)
        
        # Optionally, you can restrict available loans based on credit score
        if customer:
            self.fields['loan_type'].queryset = self.fields['loan_type'].queryset.filter(min_credit_score__lte=customer.credit_score)

    def clean(self):
        cleaned_data = super().clean()
        loan_amount = cleaned_data.get("loan_amount")
        loan_type = cleaned_data.get("loan_type")
        
        # Ensure the loan amount is within the max limit
        if loan_amount and loan_type and loan_amount > loan_type.max_amount:
            self.add_error('loan_amount', f"The loan amount cannot exceed {loan_type.max_amount}.")
        return cleaned_data
    def clean_documents(self):
        files = self.files.getlist('documents')
        valid_extensions = ['pdf', 'png', 'jpg', 'jpeg']
        max_file_size = 2 * 1024 * 1024  # 2MB in bytes

        if not files:
            raise forms.ValidationError("Please upload at least one document.")

        for file in files:
            # Validate file size
            if file.size > max_file_size:
                raise forms.ValidationError(f"{file.name} exceeds the 2MB limit.")
            
            # Validate file type
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in valid_extensions:
                raise forms.ValidationError(f"Invalid file type for {file.name}. Only {', '.join(valid_extensions).upper()} files are allowed.")

        return files[0]
    
class LoanCustomerForm(forms.ModelForm):
    class Meta:
        model = LoanCustomer
        fields = ['income', 'credit_score']
        widgets = {
            'income': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your income',
                'min': '0',
                'step': '0.01'
            }),
            'credit_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your credit score',
                'min': '0',
                'max': '850',
            }),
        }
    
    def clean_income(self):
        income = self.cleaned_data['income']
        # Validate that credit score is within a reasonable range
        if income <10000:
            raise forms.ValidationError("income should be greater than $10000")
        return income
    def clean_credit_score(self):
        credit_score = self.cleaned_data['credit_score']
        # Validate that credit score is within a reasonable range
        if credit_score < 300 or credit_score > 850:
            raise forms.ValidationError("Credit score must be between 300 and 850.")
        return credit_score

class EMIPaymentForm(forms.ModelForm):
    class Meta:
        model = EMI
        fields = ['amount_paid']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter EMI payment amount',
                'min': '0',
                'step': '0.01'
            }),
        }

    """ def clean_amount_paid(self):
        amount_paid = self.cleaned_data['amount_paid']
        loan = self.instance.loan
        
        # Ensure the amount is less than or equal to the remaining balance
        if amount_paid > loan.remaining_balance:
            raise forms.ValidationError("The payment cannot exceed the remaining balance.")
        return amount_paid """