from datetime import datetime

from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import Account
from category.models import Category
from shared.exceptions import ResourceNotFound
from transaction.models import Transaction


class TransactionData:
    def transactionData(self, transaction):
        return {
            "id": transaction.id,
            "amount": transaction.transaction_amount,
            "date": transaction.transaction_date,
            "category": transaction.category.name,
            "account": transaction.account.name,
            "description": transaction.description or "",
            "type": transaction.transaction_type,

        }


class MakeTransaction(APIView, TransactionData):
    permission_classes = (IsAuthenticated,)

    def getParams(self, payload, user):
        account = Account.objects.getAccountByName(payload.get('account'), user.id)
        category = Category.objects.getCategoryByName(payload.get('category'), user.id)
        try:
            date = datetime.strptime(payload.get("date"), "%Y-%m-%d").date()
        except:
            raise ValidationError("Invalid date format")

        return {
            "transaction_amount": payload.get("amount"),
            "user_id": user.id,
            "account": account,
            "category": category,
            "transaction_type": payload.get("type"),
            "transaction_date": date,
            "description": payload.get("description"),
        }

    def post(self, request, *args, **kwargs):
        try:

            params = self.getParams(request.data, request.user)
            with transaction.atomic():
                trn = Transaction.objects.createTransaction(params)
                print(trn.account)
                Account.objects.modifyAccountBalance(trn.account, trn.transaction_type,
                                                     trn.transaction_amount)

            return Response({"message": "Transaction created successfully!", "data": super().transactionData(trn)},
                            status=status.HTTP_201_CREATED)
        except ResourceNotFound as e:
            return Response({"message": str(e.message), "data": None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)


class GetTransactions(APIView, TransactionData):
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        transactions = Transaction.objects.filter(user_id=request.user.id)
        paginator = self.pagination_class()
        paginated_transactions = paginator.paginate_queryset(transactions, request)
        data = [super().transactionData(trn) for trn in paginated_transactions]

        return paginator.get_paginated_response(data)
