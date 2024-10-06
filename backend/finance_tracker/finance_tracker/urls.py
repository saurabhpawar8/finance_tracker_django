from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("user/", include("user.urls")),
    path("categories/", include("category.urls")),
    path("accounts/", include("account.urls")),

    path("transactions/", include("transaction.urls")),

]
