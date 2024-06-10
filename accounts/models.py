from django.db import models
from django.contrib.auth.models import User
from .constants import ACCOUNT_TYPE, GENDER
# Create your models here.


class UserBankAccount(models.Model):
    user = models.OneToOneField(
        User, related_name="account", on_delete=models.CASCADE)
    account_type = models.CharField(max_length=255, choices=ACCOUNT_TYPE)
    account_no = models.IntegerField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=150, choices=GENDER)
    initial_deposit_date = models.DateField(auto_now_add=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self) -> str:
        return str(self.account_no)


class UserAddress(models.Model):
    user = models.OneToOneField(
        User, related_name='address', on_delete=models.CASCADE)
    street_address = models.CharField(max_length=300)
    city = models.CharField(max_length=300)
    postal_code = models.IntegerField()
    country = models.CharField(max_length=300)

    def __str__(self) -> str:
        return self.user.email
