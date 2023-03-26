from django_filters import BooleanFilter, rest_framework

from .models import Recipe


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.CharFilter(
        field_name='author__id'
    )
    tags = rest_framework.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = BooleanFilter(method='get_favorite')
    is_in_shopping_cart = BooleanFilter(method='get_shopping')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def get_favorite(self, queryset, query_param, value):
        user = self.request.user
        if value:
            queryset = queryset.filter(favorite__user__username=user)
            return queryset
        queryset = queryset.exclude(favorite__user__username=user)
        return queryset

    def get_shopping(self, queryset, query_param, value):
        user = self.request.user
        if value:
            queryset = queryset.filter(recipes_cart__user__username=user)
            return queryset
        queryset = queryset.exclude(recipes_cart__user__username=user)
        return queryset
