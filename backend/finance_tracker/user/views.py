from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, status
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView

from user.serializers import MyTokenObtainPairSerializer


class AddUser(APIView):

    def post(self, request, *args, **kwargs):
        try:
            payload = request.data
            email = payload.get('email')
            password = payload.get('password')
            print(email.split('@'))
            try:
                username = email.split('@')[0]
            except:
                raise ValidationError('Please enter a valid email address.')

            user = User.objects.create(email=email, username=username)
            user.set_password(password)
            user.save()
            return Response({"message": f"Succesfully created user with username {username}!"},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
