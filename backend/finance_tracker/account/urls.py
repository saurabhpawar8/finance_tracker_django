from django.urls import path
from account.views import AddAccount, GetAccounts, GetAccountById, GetAccountByName, DeleteAccount, UpdateAccount

urlpatterns = [
    path("add/", AddAccount.as_view()),
    path("all/", GetAccounts.as_view()),
    path("<str:id>/by-id/", GetAccountById.as_view()),
    path("<str:id>/by-name/", GetAccountByName.as_view()),
    path("<str:id>/delete/", DeleteAccount.as_view()),
    path("<str:id>/update/", UpdateAccount.as_view()),
]
