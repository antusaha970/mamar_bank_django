from django.db import models
from accounts.models import UserBankAccount
# Create your models here.

TRANSACTION_TYPE = (
    (1, 'Deposit'),
    (2, 'Withdrawal'),
    (3, 'Loan'),
    (4, 'Loan paid')
)


class Transactions(models.Model):
    account = models.ForeignKey(
        UserBankAccount, related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after_transaction = models.DecimalField(
        max_digits=12, decimal_places=2)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approval = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']
