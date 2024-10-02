from django.contrib.auth.models import User
from django.db import models

from shared.exceptions import ResourceNotFound


class CategoryManager(models.Manager):
    def createCategory(self, params):
        self.create(**params)

    def getCategories(self, user_id):
        return list(self.filter(user_id=user_id).values_list("name", flat=True))

    def getCategoryById(self, id, user_id):
        try:
            category = self.get(id=id, user_id=user_id)
        except:
            raise ResourceNotFound("Category not found")
        return category

    def getCategoryByName(self, name, user_id):
        try:
            category = self.get(name=name, user_id=user_id)
        except:
            raise ResourceNotFound("Category not found")
        return category




class Category(models.Model):
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category')
    objects = CategoryManager()

    def __str__(self):
        return self.name
