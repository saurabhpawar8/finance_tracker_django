from os.path import pathsep

from django.urls import path, re_path

from transaction.views import GetTransactions, MakeTransaction, GetTransaction

urlpatterns = [
    path("add/", MakeTransaction.as_view()),
    path("all/", GetTransactions.as_view()),
    re_path(r"(?P<id>\d*)/by-id/$", GetTransaction.as_view()),
]
