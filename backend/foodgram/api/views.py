from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, mixins, pagination, status, \
    generics
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .models import Ingredient, Tag, User, Follow
from .serializers import (IngredientSerializer, TagSerializer, UserSerializer,
                          SetPasswordSerializer, CreateUserSerializator, SubsciptionsSerializer)
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
            return Response({'status': 'password set'})
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def subsciptions(self, request):
        user = self.request.user
        subscriptions = user.follower.select_related('author').order_by('id')
        pages = self.paginate_queryset(subscriptions)
        serializer = SubsciptionsSerializer(pages, many=True, context={'request':request})
        return self.get_paginated_response(serializer.data)


class FavoriteViewSet(viewsets.GenericViewSet,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin):
    pass
