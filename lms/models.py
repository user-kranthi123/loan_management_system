from django.db import models
from customer import models as CUST_MODEL
# Create your models here.
class LoanType(models.Model):
    name = models.CharField(max_length=50)
    max_amount = models.DecimalField(max_digits=15, decimal_places=2)  # Max loan limit
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Loan interest rate
    max_tenure_years=models.IntegerField(default=5)
    min_credit_score = models.IntegerField() #Minimum CreditScore
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name

class LoanCustomer(models.Model):
    customer = models.ForeignKey(CUST_MODEL.Customer, on_delete=models.CASCADE)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    credit_score = models.IntegerField()

    def __str__(self):
        return f"{self.customer.user}-{self.id}"

class LoanApplication(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    customer = models.ForeignKey(LoanCustomer, on_delete=models.CASCADE)
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE)
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2)
    application_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True)  # Admin's notes on the application
    documents = models.FileField(upload_to='loan_documents/', blank=True, null=True)  # Add document upload field
    s3_document_url=models.CharField(max_length=1024, blank=True, null=True)
    def __str__(self):
        return f"Application {self.loan_type}-#{self.id}"
    
class Loan(models.Model):
    STATUS_CHOICES = [
        ('PENDING','Pending'),
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('OVERDUE', 'Overdue'),
    ]
    application = models.OneToOneField(LoanApplication, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    loan_term_months = models.IntegerField()
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    remaining_balance = models.DecimalField(max_digits=15, decimal_places=2)
    emi_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    def __str__(self):
        return f"Loan {self.application.loan_type}-#{self.id} "

class EMI(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    payment_date = models.DateField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_balance_after_payment = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"Payment-#{self.id}"