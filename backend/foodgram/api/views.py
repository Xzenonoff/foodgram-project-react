import csv
import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, mixins, pagination, status, \
    generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Ingredient, Tag, User, Follow, Recipe, Favorite, Cart, \
    IngredientQuantity
from .serializers import (IngredientSerializer, TagSerializer, UserSerializer,
                          SetPasswordSerializer, CreateUserSerializator,
                          SubsciptionsSerializer, RecipeSerializer,
                          RecipesSerializer,
                          FavoriteSerializer)
from rest_framework.response import Response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class UserViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializator
        return UserSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.user.is_anonymous:
            return Response(status=401)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def set_password(self, request, pk=None):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        user = self.request.user
        subscriptions = user.follower.select_related('author').order_by('id')
        pages = self.paginate_queryset(subscriptions)
        serializer = SubsciptionsSerializer(pages, many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        user = self.request.user
        author = get_object_or_404(User, id=pk)
        if user == author:
            return Response(
                {'errors': 'Вы не можете подписываться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'POST':
            if Follow.objects.filter(follower=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            author = get_object_or_404(User, id=pk)
            follower = Follow.objects.create(follower=user, author=author)
            serializer = SubsciptionsSerializer(follower,
                                                context={'request': request})
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
    http_method_names = ['get', 'post', 'delete', 'patch']
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe__id=pk).exists():
                return Response(
                    {
                        'errors': 'Рецепт уже добавлен в список'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe = get_object_or_404(Recipe, pk=pk)
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        obj = Favorite.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {
                'errors': 'Рецепт уже удален'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        if request.method == 'POST':
            if Cart.objects.filter(user=user, recipe__id=pk).exists():
                return Response(
                    {'errors': 'Этот рецепт уже в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe = get_object_or_404(Recipe, id=pk)
            Cart.objects.create(user=user, recipe=recipe)
            serializer = RecipesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        obj = Cart.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Этого рецепта нет в вашей корзине'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = self.request.user
        ingredients = IngredientQuantity.objects.filter(
            recipe__recipes_cart__user=user
        ).values(
            'amount', 'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            ingredient_amount=Sum('amount')).values_list(
            'ingredient__name',
            'ingredient_amount',
            'ingredient__measurement_unit'
        )

        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=ShoppingCart.pdf'},
        )
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        for product in list(ingredients):
            writer.writerow(product)
        return response
