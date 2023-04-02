from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (Cart, Favorite, Follow, Ingredient, IngredientQuantity,
                     Recipe, Tag, User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username',)
    list_display = ('username', 'email',)
    search_fields = ('username', 'email',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('author', 'tags', 'name',)
    list_display = ('name', 'author', 'favorited_counter',)
    search_fields = ('name', 'author__username', 'tags__name',)

    def favorited_counter(self, obj):
        return obj.favorite.count()


class IngredientImportResource(resources.ModelResource):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    resource_classes = (IngredientImportResource,)
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(Tag)
admin.site.register(Follow)
admin.site.register(IngredientQuantity)
admin.site.register(Favorite)
admin.site.register(Cart)
