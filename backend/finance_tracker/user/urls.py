from django.urls import path

from user.views import AddUser, MyTokenObtainPairView

urlpatterns = [
    path("signup/", AddUser.as_view()),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),

]
