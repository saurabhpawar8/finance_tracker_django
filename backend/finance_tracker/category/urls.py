from category.views import AddCategory, GetCategories, GetCategoryById, DeleteCategory, UpdateCategory
from django.urls import path

urlpatterns = [
    path("add/", AddCategory.as_view()),
    path("all/", GetCategories.as_view()),
    path("<str:id>/by-id/", GetCategoryById.as_view()),
    path("<str:id>/by-name/", GetCategoryById.as_view()),
    path("<str:id>/delete/", DeleteCategory.as_view()),
    path("<str:id>/update/", UpdateCategory.as_view()),
]
