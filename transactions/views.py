from typing import Any
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Transactions
from .contants import DEPOSIT, LOAN, LOAN_PAID, WITHDRAWAL
from .forms import DepositForm, WithdrawalForm, LoanRequestForm
# Create your views here.


def send_main_to_user(subject, user, amount, template_name):
    message = render_to_string(template_name, {
        'user': user,
        'amount': amount
    })
    send_mail = EmailMultiAlternatives(
        subject, '', to=[user.email])
    send_mail.attach_alternative(message, 'text/html')
    send_mail.send()


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy("transaction_report")
    title = ''
    model = Transactions

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context


class DepositMoneyView(TransactionCreateMixin):
    success_url = reverse_lazy("transaction_report")
    title = 'Deposit Money'

    form_class = DepositForm

    def get_initial(self):
        initial = {
            'transaction_type': DEPOSIT
        }
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account

        account.balance += amount
        account.save(update_fields=['balance'])
        messages.success(self.request, f"""{
                         amount} is deposited to your account """)
        send_main_to_user("Deposit conformation", self.request.user,
                          amount, "transactions/deposit_mail.html")
        return super().form_valid(form)


class WithdrawalMoneyView(TransactionCreateMixin):
    success_url = reverse_lazy("transaction_report")
    title = 'Withdraw Money'

    form_class = WithdrawalForm

    def get_initial(self):
        initial = {
            'transaction_type': WITHDRAWAL
        }
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account

        account.balance -= amount
        account.save(update_fields=['balance'])

        messages.success(self.request, f"""{
                         amount} is withdrawn from your account """)
        send_main_to_user("Withdrawal notice", self.request.user,
                          amount, "transactions/withdrawal_mail.html")
        return super().form_valid(form)


class LoanMoneyView(TransactionCreateMixin):
    title = 'Request For Loan'

    form_class = LoanRequestForm

    def get_initial(self):
        initial = {
            'transaction_type': LOAN
        }
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')

        current_loan_count = Transactions.objects.filter(
            account=self.request.user.account, loan_approval=True, transaction_type=LOAN).count()

        if current_loan_count >= 3:
            return HttpResponse("Loan limit exceeded")

        messages.success(self.request, f"""Loan request for {
                         amount} successfully sent""")
        send_main_to_user("Loan request notice", self.request.user,
                          amount, "transactions/loan_mail.html")
        return super().form_valid(form)


class TransactionReportView(LoginRequiredMixin, ListView):
    model = Transactions
    template_name = 'transactions/transaction_report.html'
    balance = 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )

        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            queryset = queryset.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date)

            self.balance = Transactions.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["account"] = self.request.user.account
        return context


class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transactions, id=loan_id)

        if loan.loan_approval:
            user_account = loan.account
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('transaction_report')
            else:
                return redirect('transaction_report')


class LoanListView(LoginRequiredMixin, ListView):
    model = Transactions
    template_name = 'transactions/loan_request.html'
    context_object_name = 'loans'

    def get_queryset(self):
        user = self.request.user.account
        queryset = Transactions.objects.filter(
            account=user, transaction_type=LOAN)
        return queryset
