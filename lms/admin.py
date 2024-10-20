from django.contrib import admin
from . import models as LOAN_MODEL
# Register your models here.
admin.site.register(LOAN_MODEL.Loan)
admin.site.register(LOAN_MODEL.LoanCustomer)
admin.site.register(LOAN_MODEL.LoanApplication)
admin.site.register(LOAN_MODEL.LoanType)
admin.site.register(LOAN_MODEL.EMI)