import csv

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import (
    Cart, Favorite, Follow, Ingredient, IngredientQuantity, Recipe, Tag, User
)
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import (
    IngredientSerializer, RecipesAndFavoriteSerializer, RecipeSerializer,
    SubsciptionsSerializer, TagSerializer, UserSerializer
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class UserViewSet(DjoserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination
    http_method_names = ('get', 'post', 'delete',)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        if request.user.is_anonymous:
            return Response(status=401)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        pagination_class=LimitPageNumberPagination
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(following__follower=request.user)
        pages = self.paginate_queryset(subscriptions)
        serializer = SubsciptionsSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        serializer_class=SubsciptionsSerializer
    )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubsciptionsSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            if not serializer.is_valid():
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(follower=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        obj = Follow.objects.filter(follower=user, author=author)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на этого пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrAuthorOrReadOnly)
    http_method_names = ('get', 'post', 'delete', 'patch',)
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    queryset = Recipe.objects.all()
    pagination_class = LimitPageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.create_obj(request.user, pk, Favorite)
        return self.delete_obj(request.user, pk, Favorite)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.create_obj(request.user, pk, Cart)
        return self.delete_obj(request.user, pk, Cart)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        ingredients = IngredientQuantity.objects.filter(
            recipe__recipes_cart__user=user
        ).values(
            'amount', 'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            ingredient_amount=Sum('amount')
        ).values_list(
            'ingredient__name',
            'ingredient_amount',
            'ingredient__measurement_unit'
        )
        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=ShoppingCart.csv'}
        )
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        for product in list(ingredients):
            writer.writerow(product)
        return response

    @staticmethod
    def create_obj(user, pk, model):
        recipe = get_object_or_404(Recipe, pk=pk)
        _, created = model.objects.get_or_create(user=user, recipe=recipe)
        if created:
            serializer = RecipesAndFavoriteSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response({'errors': 'Этот рецепт уже добавлен'})

    @staticmethod
    def delete_obj(user, pk, model):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        error_message = (
            'Рецепт уже удален'if model == Favorite else
            'Этого рецепта нет в вашей корзине'
        )
        return Response(
            {
                'errors': error_message
            },
            status=status.HTTP_400_BAD_REQUEST
        )
