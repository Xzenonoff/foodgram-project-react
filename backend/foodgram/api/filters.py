from distutils.util import strtobool

from django_filters import rest_framework

from .models import Favorite, Recipe, Cart, Tag
from .utils import check_user_and_request

CHOICES_LIST = (
    ('0', 'False'),
    ('1', 'True')
)


class RecipeFilter(rest_framework.FilterSet):
    is_favorited = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST,
        method='is_favorited_method'
    )
    is_in_shopping_cart = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST,
        method='is_in_shopping_cart_method'
    )
    author = rest_framework.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def is_favorited_method(self, queryset, name, value):
        check_result, user = check_user_and_request(self.request)
        if check_result is False:
            return Recipe.objects.none()

        favorites = Favorite.objects.filter(user=user)
        recipes = [item.recipe.id for item in favorites]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=recipes)

    def is_in_shopping_cart_method(self, queryset, name, value):
        check_result, user = check_user_and_request(self.request)
        if check_result is False:
            return Recipe.objects.none()

        shopping_cart = Cart.objects.filter(user=user)
        recipes = [item.recipe.id for item in shopping_cart]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=recipes)

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
