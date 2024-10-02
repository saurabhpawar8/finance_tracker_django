from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from unicodedata import category

from account.views import AccountData
from category.models import Category
from shared.exceptions import AlreadyExists, ResourceNotFound


class AddCategory(APIView):
    permission_classes = (IsAuthenticated,)

    def getParams(self, payload, user):

        return {
            "name": payload.get("name"),
            "user_id": user.id,
        }

    def post(self, request, *args, **kwargs):
        try:
            params = self.getParams(request.data, request.user)
            if Category.objects.filter(**params).exists():
                raise AlreadyExists("Category already exists")
            with transaction.atomic():
                Category.objects.createCategory(params)
            return Response({"message": "Category created successfully!"}, status=status.HTTP_201_CREATED)

        except AlreadyExists as e:
            return Response({"message": str(e.message)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_400_BAD_REQUEST)


class GetCategories(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            categories = Category.objects.getCategories(request.user.id)
            return Response({"message": "All Categories", "data": categories}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)


class CategoryData:
    def categoryData(self, category):
        return {
            "id": category.id,
            "name": category.name,
        }


class GetCategoryById(APIView, CategoryData):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, *args, **kwargs):
        try:
            category = Category.objects.getCategoryById(id, request.user.id)
            return Response({"message": "Category found", "data": super().categoryData(category)},
                            status=status.HTTP_200_OK)
        except ResourceNotFound as e:
            return Response({"message": str(e.message), "data": None}, status=status.HTTP_404_NOT_FOUND)


class GetCategoryByName(APIView, CategoryData):
    permission_classes = (IsAuthenticated,)

    def get(self, request, name, *args, **kwargs):
        try:
            category = Category.objects.getCategoryByName(name, request.user.id)

            return Response({"message": "Category found", "data": super().categoryData(category)},
                            status=status.HTTP_200_OK)
        except ResourceNotFound as e:
            return Response({"message": str(e.message), "data": None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)


class DeleteCategory(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, id, *args, **kwargs):
        try:
            category = Category.objects.getCategoryById(id, request.user.id)
            if category:
                category.delete()
            return Response({"message": "Category deleted succesfully!", "data": None},
                            status=status.HTTP_200_OK)
        except ResourceNotFound as e:
            return Response({"message": str(e.message), "data": None}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)


class UpdateCategory(APIView, CategoryData):
    permission_classes = (IsAuthenticated,)

    def put(self, request, id, *args, **kwargs):
        try:
            category = Category.objects.getCategoryById(id, request.user.id)
            with transaction.atomic():
                if category:
                    category.name = request.data.get('name')
                    category.save(update_fields=['name'])

            return Response({"message": "Category updated successfully!", "data": super().categoryData(category)},
                            status=status.HTTP_200_OK)


        except ResourceNotFound as e:
            return Response({"message": str(e.message), "data": None}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": str(e), "data": None}, status=status.HTTP_400_BAD_REQUEST)
