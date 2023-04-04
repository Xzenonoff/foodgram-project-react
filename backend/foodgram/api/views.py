from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import Cart, Favorite, Follow, Ingredient, Recipe, Tag, User
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipesAndFavoriteSerializer,
                          RecipeSerializer, SubsciptionsSerializer,
                          TagSerializer, UserSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


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
        shopping_cart = Cart.objects.filter(user=request.user).all()
        shopping_list = {}
        for item in shopping_cart:
            for ingredient in item.recipe.recipes.all():
                name = ingredient.ingredient.name
                measurement_unit = (
                    ingredient.ingredient.measurement_unit
                )
                amount = ingredient.amount
                if name not in shopping_list:
                    shopping_list[name] = {
                        'name': name,
                        'measurement_unit': measurement_unit,
                        'amount': amount
                    }
                else:
                    shopping_list[name]['amount'] += amount
        content = (
            [
                f'{item["name"]}({item["measurement_unit"]})'
                f'-{item["amount"]}\n'
                for item in shopping_list.values()
            ]
        )
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format('cart.txt')
        )
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
            'Рецепт уже удален' if model == Favorite else
            'Этого рецепта нет в вашей корзине'
        )
        return Response(
            {
                'errors': error_message
            },
            status=status.HTTP_400_BAD_REQUEST
        )
