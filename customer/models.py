from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10)
    profile_pic = models.ImageField(upload_to='profile_pics/customer/',null=True, blank=True)
    s3_document_url=models.CharField(max_length=1024, blank=True, null=True)
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return self.user.username