from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)


class Tag(models.Model):
    slug = models.SlugField(unique=True, max_length=200)
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measure_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=50)
    image = models.ImageField()
    description = models.TextField()
    cooking_time = models.PositiveSmallIntegerField()
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientQuantity',
        through_fields=('recipe', 'ingredient'),
    )

    def __str__(self):
        return self.name


class IngredientQuantity(models.Model):
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )

    class Meta:
        unique_together = ('author', 'follower')
