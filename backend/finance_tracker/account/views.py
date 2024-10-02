from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import Account
from category.models import Category
from shared.exceptions import AlreadyExists, ResourceNotFound


class AddAccount(APIView):
    permission_classes = (IsAuthenticated,)

    def getParams(self, payload, user):

        return {
            "name": payload.get("name"),
            "user_id": user.id,
            "balance": payload.get("balance"),
        }

    def post(self, request, *args, **kwargs):
        try:
            params = self.getParams(request.data, request.user)
            if Account.objects.filter(**params).exists():
                raise AlreadyExists("Account already exists")
            with transaction.atomic():
                Account.objects.createAccount(params)
            return Response({"message": "Account created successfully!"}, status=status.HTTP_201_CREATED)

        except AlreadyExists as e:
            return Response({"message": str(e.message)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_400_BAD_REQUEST)


class GetAccounts(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            accounts = Account.objects.getAccounts(request.user.id)
            return Response({"message": "All accounts", "data": accounts}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)


class AccountData:
    def accountData(self, account):
        return {
            "id": account.id,
            "name": account.name,
            "balance": account.balance
        }


class GetAccountById(APIView, AccountData):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, *args, **kwargs):
        try:
            account = Account.objects.getAccountById(id, request.user.id)
            return Response({"message": "Account found", "data": super().accountData(account)},
                            status=status.HTTP_200_OK)
        except ResourceNotFound as e:
            return Response({"message": str(e.message), "data": None}, status=status.HTTP_404_NOT_FOUND)


class GetAccountByName(APIView, AccountData):
    permission_classes = (IsAuthenticated,)

    def get(self, request, name, *args, **kwargs):
        try:
            account = Account.objects.getAccountByName(name, request.user.id)

            return Response({"message": "Category found", "data": super().accountData(account)},
                            status=status.HTTP_200_OK)
        except ResourceNotFound as e:
            return Response({"message": str(e.message), "data": None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccount(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, id, *args, **kwargs):
        try:
            Category.objects.deleteAccount(id, request.user.id)

            return Response({"message": "Account deleted successfully!", "data": None},
                            status=status.HTTP_200_OK)
        except ResourceNotFound as e:
            return Response({"message": str(e.message), "data": None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)


class UpdateAccount(APIView, AccountData):
    permission_classes = (IsAuthenticated,)

    def update(self, request, id, *args, **kwargs):
        try:
            account = Account.objects.getAccountById(id, request.user.id)
            with transaction.atomic():
                if account:
                    account.name = request.data.get('name')
                    account.balance = request.data.get('balance')
                    account.save(update_fields=['name'])
            return Response({"message": "Account updated successfully!", "data": super().accountData(account)},
                            status=status.HTTP_200_OK)


        except ResourceNotFound as e:
            return Response({"message": str(e.message), "data": None}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)
