from django.db import models
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

from account.models import Account
from category.models import Category
from shared.exceptions import ResourceNotFound


class TransactionManager(models.Manager):
    def createTransaction(self, params):
        return self.create(**params)

    def getTransactionById(self, id):
        try:
            return self.get(id=id)
        except:
            raise ResourceNotFound("Transaction does not exist")

    def getTransactions(self, params):
        try:
            return Transaction.objects.filter(**params)
        except:
            raise ResourceNotFound("Transaction does not exist")

    def getTrasactionByAmountStatus(self, user_id, amount_status):
        return self.get(user_id=user_id, amount_status=amount_status)

    def getTrasactionByTransactionNumber(self, transaction_number, user_id):
        try:
            return self.get(transaction_number=transaction_number, user_id=user_id)
        except:
            raise ResourceNotFound("Transaction does not exist")


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
        ('Transfer', 'Transfer'),
    ]
    AMOUNT_STATUS = [
        ('Debit', 'Debit'),
        ('Credit', 'Credit'),
    ]
    transaction_number = models.CharField(max_length=50, unique=True)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_date = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='accounts_transactions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_transactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_transactions')
    amount_status = models.CharField(max_length=10, choices=AMOUNT_STATUS)
    objects = TransactionManager()

    def __str__(self):
        return str(self.pk)


class TransactionNumberManager(models.Manager):

    def createTransactionNumber(self, transaction_number, user_id):
        self.create(last_number=transaction_number, user_id=user_id)

    def generateTransactionNumber(self, user):
        if not self.filter(user_id=user.id).exists():
            self.createTransactionNumber("TRN1", user.id)
            return "TRN1"
        else:
            last_trn_number = self.get(user_id=user.id)
            trn_no = last_trn_number.last_number
            new_trn_no = f"TRN{int(trn_no[3:]) + 1}"
            last_trn_number.last_number = new_trn_no
            last_trn_number.save(update_fields=['last_number'])
            return new_trn_no


class TransactionNumber(models.Model):
    last_number = models.CharField(max_length=50)
    user_id = models.CharField(max_length=50)
    objects = TransactionNumberManager()

    def __str__(self):
        return self.last_number
