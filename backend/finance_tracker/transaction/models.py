from django.db import models
from django.contrib.auth.models import User
from account.models import Account
from category.models import Category


class TransactionManager(models.Manager):
    def createTransaction(self, params):
        return self.create(**params)


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_date = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='accounts_transactions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_transactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_transactions')
    objects = TransactionManager()

    def __str__(self):
        return str(self.pk)
