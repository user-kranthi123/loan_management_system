"""loan_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth.views import LogoutView
from lms import views as lms_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lms_view.home_view, name='home_page'),
    path('customer/',include('customer.urls')),
    path('load_data',lms_view.load_sample_data, name='load_sample_data'),
    path('postlogin', lms_view.post_login_view, name='postlogin'),
    path('view_loan_types',lms_view.view_all_loan_types,name='view_all_loans_types'),
    path('get-customer-eligibility/<int:pk>', lms_view.check_loan_eligibility, name='check_customer_eligibility'),
    path('logout', LogoutView.as_view(template_name='home/base.html'),name='logout'),
]
