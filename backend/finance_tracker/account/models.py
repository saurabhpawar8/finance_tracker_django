from decimal import Decimal

from django.db import models
from django.db.models import ForeignKey
from django.contrib.auth.models import User
from unicodedata import decimal

from shared.exceptions import ResourceNotFound


class AccountManager(models.Manager):
    def createAccount(self, params):
        self.create(**params)

    def getAccounts(self, user_id):
        return list(self.filter(user_id=user_id).values_list("name", flat=True))

    def getAccountById(self, id, user_id):
        try:
            account = self.get(id=id, user_id=user_id)
        except:
            raise ResourceNotFound("Account not found")
        return account

    def getAccountByName(self, name, user_id):
        try:
            account = self.get(name=name, user_id=user_id)
        except:
            raise ResourceNotFound("Account not found")
        return account

    def incrementAccountBalance(self, account, amount):
        account.balance += amount
        account.save(update_fields=["balance"])

    def decrementAccountBalance(self, account, amount):
        account.balance -= amount
        account.save(update_fields=["balance"])

    def updateTransferAccountBalance(self, from_account, to_account, amount):
        from_account.balance -= amount
        to_account.balance += amount
        from_account.save(update_fields=["balance"])
        to_account.save(update_fields=["balance"])

    def modifyAccountBalanceIfTransactionTypeDiff(self, transaction_type, amount, previous_amt, account):
        if transaction_type == "Income":
            account.balance += (previous_amt + amount)
            account.save(update_fields=["balance"])
        elif transaction_type == "Expense":
            account.balance -= (previous_amt - amount)
            account.save(update_fields=["balance"])


class Account(models.Model):
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    user = ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    objects = AccountManager()

    def __str__(self):
        return self.name
