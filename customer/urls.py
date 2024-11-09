from django.urls import path
from django.contrib.auth.views import LoginView
from customer import views

urlpatterns = [
     path('login', views.login_view, name='login_page'),
     path('signup', views.signup_page_view, name = 'customer_signup'),
     path('dashboard', views.dashboard_view, name= 'customer_dashboard'),
     path('apply-for-loan', views.apply_for_loan, name='apply_for_loan'),
     path('pay-emi/<int:pk>', views.pay_emi_view,name='pay_emi'),
     path('update-details', views.update_loan_customer, name='update_loan_customer'),
     path('loan-details',views.loan_details_view,name='loan-details')
]