from os.path import pathsep

from django.urls import path

from transaction.views import GetTransactions, MakeTransaction

urlpatterns = [
path("add/", MakeTransaction.as_view()),
    path("all/", GetTransactions.as_view()),
]
