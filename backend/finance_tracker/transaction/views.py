from datetime import datetime, timedelta

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Max
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from unicodedata import category

from account.models import Account
from category.models import Category
from shared.exceptions import ResourceNotFound
from transaction.models import Transaction, TransactionNumber


class TransactionData:
    def transactionData(self, transaction):
        return {
            "id": transaction.id,
            "amount": transaction.transaction_amount,
            "date": transaction.transaction_date.strftime("%Y-%m-%d"),
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

        transaction_number = TransactionNumber.objects.generateTransactionNumber(user)

        return {
            "transaction_amount": payload.get("amount"),
            "user_id": user.id,
            "account": account,
            "category": category,
            "transaction_type": payload.get("type"),
            "transaction_date": date,
            "description": payload.get("description"),
            "transaction_number": transaction_number,
        }

    def post(self, request, *args, **kwargs):
        try:

            with transaction.atomic():
                params = self.getParams(request.data, request.user)
                trn = Transaction.objects.createTransaction(params)
                if trn.transaction_type == "Income":
                    Account.objects.updateIncomeAccountBalance(trn.account, trn.transaction_amount)
                else:
                    Account.objects.updateExpenseAccountBalance(trn.account, trn.transaction_amount)

            return Response({"message": "Transaction created successfully!", "data": super().transactionData(trn)},
                            status=status.HTTP_201_CREATED)
        except ResourceNotFound as e:
            return Response({"message": str(e.message), "data": None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)


class MakeTransferTransaction(APIView, TransactionData):
    permission_classes = (IsAuthenticated,)

    def getParams(self, payload, user):
        from_account = Account.objects.getAccountByName(payload.get('from_account'), user.id)
        to_account = Account.objects.getAccountByName(payload.get('to_account'), user.id)
        try:
            date = datetime.strptime(payload.get("date"), "%Y-%m-%d").date()
        except:
            raise ValidationError("Invalid date format")
        transaction_number = TransactionNumber.objects.generateTransactionNumber(user)

        param1 = {
            "transaction_amount": payload.get("amount"),
            "user_id": user.id,
            "account": from_account,
            "transaction_type": "Transfer",
            "transaction_date": date,
            "description": payload.get("description"),
            "transaction_number": transaction_number,
        }
        param2 = {
            "transaction_amount": payload.get("amount"),
            "user_id": user.id,
            "account": to_account,
            "transaction_type": "Transfer",
            "transaction_date": date,
            "description": payload.get("description"),
            "transaction_number": transaction_number,
        }
        return param1, param2

    def post(self, request, *args, **kwargs):
        try:

            with transaction.atomic():
                param1, param2 = self.getParams(request.data, request.user)
                trn1 = Transaction.objects.createTransaction(param1)
                trn2 = Transaction.objects.createTransaction(param2)
                Account.objects.updateTransferAccountBalance(trn1.account, trn2.account, param1["transaction_amount"])

            return Response({"message": "Transaction created successfully!", "data": None},
                            status=status.HTTP_201_CREATED)
        except ResourceNotFound as e:
            return Response({"message": str(e.message), "data": None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)


class GetTransactions(APIView):
    permission_classes = (IsAuthenticated,)

    def getDateRange(self, range):
        today = datetime.now()
        if range == "Last Month":
            from_date = (today.replace(day=1) - timedelta(days=1)).date()
            to_date = (today.replace(day=1) - timedelta(days=1)).date()
        elif range == "Last Year":
            from_date = today.replace(year=today.year - 1, month=1, day=1).date()
            to_date = today.replace(year=today.year - 1, month=12, day=31).date()
        return from_date, to_date

    def getParams(self, query_params, user):

        category = query_params.get("category")
        account = query_params.get("account")
        from_dt = query_params.get("from_date")
        to_dt = query_params.get("to_date")
        params = {
            "user_id": user.id
        }
        range = query_params.get("range")

        if from_dt and to_dt:
            try:
                from_date = datetime.strptime(from_dt, "%Y-%m-%d").date()
                to_date = datetime.strptime(to_dt, "%Y-%m-%d").date()
            except:
                raise ValidationError("Invalid date format")
            params["transaction_date__range"] = (from_date, to_date)
        elif range:
            from_date, to_date = self.getDateRange(range)
            params["transaction_date__range"] = (from_date, to_date)
        if category:
            params["category__name"] = category
        if account:
            params["account__name"] = account

        return params

    def get(self, request, *args, **kwargs):
        try:

            params = self.getParams(request.GET, request.user)
            page_no = request.GET.get("page")

            transactions = Transaction.objects.getTransactions(params)

            paginator = Paginator(transactions, 50)
            page_object = paginator.get_page(page_no)

            obj = TransactionData()
            result = [obj.transactionData(trn) for trn in page_object]

            data = {
                "total_pages": paginator.num_pages,
                "current_page": page_object.number,
                "has_next": page_object.has_next(),
                "has_previous": page_object.has_previous(),
                "data": result
            }
            return Response({"message": "All transactions", "data": data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)


class GetTransaction(APIView, TransactionData):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, *args, **kwargs):
        try:
            if not id:
                raise ValidationError("Please provide id of transaction")
            trn = Transaction.objects.getTransactionById(id)
            data = super().transactionData(trn)
            return Response({"message": "Transaction Found", "data": data}, status=status.HTTP_200_OK)

        except ResourceNotFound as e:
            return Response({"message": str(e.message), "data": None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)


class UpdateTransaction(APIView, TransactionData):
    permission_classes = (IsAuthenticated,)

    def put(self, request, id, *args, **kwargs):
        try:
            payload = request.data
            if not id:
                raise ValidationError("Please provide id of transaction")
            with transaction.atomic():
                trn = Transaction.objects.getTransactionById(id)
                category = Category.objects.getCategoryByName(payload.get("category"))
                account = Account.objects.getAccountByName(payload.get("account"))
                date = datetime.strptime(payload.get("date"), "%Y-%m-%d").date()

                previous_amt = trn.transaction_amount
                amount = payload.get("amount")
                previous_transaction_type = trn.transaction_type
                transaction_type = payload.get("type")

                if previous_transaction_type == "Transfer":
                    trn2 = Transaction.objects.getTrasactionByTransactionNumber(trn.transaction_number, trn.user.id)
                    if trn.amount_status == "Credit":
                        Account.objects.incrementAccountBalance(trn2.account, trn2.amount)
                        Account.objects.decrementAccountBalance(trn.account, trn.amount)
                    else:
                        Account.objects.incrementAccountBalance(trn.account, trn.amount)
                        Account.objects.decrementAccountBalance(trn2.account, trn2.amount)

                if previous_transaction_type != transaction_type:
                    Account.objects.modifyAccountBalanceIfTransactionTypeDiff(transaction_type, amount, previous_amt,
                                                                              account)
                else:
                    Account.objects.modifyAccountBalance(account, amount)

                trn.transaction_date = date
                trn.transaction_amount = payload.get("amount")
                trn.description = payload.get("description")
                trn.transaction_type = payload.get("type")
                trn.category = category
                trn.account = account
                trn.save(
                    update_fields=["transaction_date", "transaction_amount", "description", "transaction_type",
                                   "category",
                                   "account"])
            return Response({"message": "Transaction Updated", "data": super().transactionData(trn)},
                            status=status.HTTP_200_OK)
        except ResourceNotFound as e:
            return Response({"message": str(e.message), "data": None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)


class DeleteTransaction(APIView, TransactionData):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, id, *args, **kwargs):
        try:
            if not id:
                raise ValidationError("Please provide id of transaction")
            trn = Transaction.objects.getTransactionById(id)
            if trn.transaction_type == "Income":
                Account.objects.incrementAccountBalance(trn.account, trn.amount)
            elif trn.transaction_type == "Expense":
                Account.objects.decrementAccountBalance(trn.account, trn.amount)

            trn.delete()
            return Response({"message": "Transaction Deleted", "data": None}, status=status.HTTP_200_OK)
        except ResourceNotFound as e:
            return Response({"message": str(e.message), "data": None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)


class DeleteTransferTransaction(APIView, TransactionData):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, id, *args, **kwargs):
        try:
            if not id:
                raise ValidationError("Please provide id of transaction")
            trn1 = Transaction.objects.getTransactionById(id)
            amount_status = "Debit" if trn1.amount_status == "Credit" else "Credit"
            trn2 = Transaction.objects.getTrasactionByAmountStatus(trn1.user.id, amount_status)
            if amount_status == "Credit":
                Account.objects.incrementAccountBalance(trn1.account, trn1.amount)
                Account.objects.decrementAccountBalance(trn2.account, trn2.amount)
            else:
                Account.objects.decrementAccountBalance(trn1.account, trn1.amount)
                Account.objects.incrementAccountBalance(trn2.account, trn2.amount)

            trn1.delete()
            trn2.delete()
            return Response({"message": "Transaction Deleted", "data": None}, status=status.HTTP_200_OK)
        except ResourceNotFound as e:
            return Response({"message": str(e.message), "data": None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)
