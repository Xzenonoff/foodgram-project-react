from django.contrib import admin
from .models import Ingredient, Recipe, Tag, Follow, IngredientQuantity, Favorite, User, Cart

admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Follow)
admin.site.register(IngredientQuantity)
admin.site.register(Favorite)
admin.site.register(User)
admin.site.register(Cart)