from typing import Any
from django.contrib import admin
from .models import Transactions
from .views import send_main_to_user
# Register your models here.


@admin.register(Transactions)
class TransactionModelAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'balance_after_transaction',
                    'transaction_type', 'loan_approval']

    def save_model(self, request, obj, form, change):
        obj.account.balance += obj.amount
        obj.balance_after_transaction = obj.account.balance

        obj.account.save()
        send_main_to_user("Loan approval", obj.account.user,
                          obj.amount, 'transactions/admin_mail.html')

        super().save_model(request, obj, form, change)
