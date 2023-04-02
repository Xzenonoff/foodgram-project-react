from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer as DjoserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status

from .models import (Cart, Favorite, Follow, Ingredient, IngredientQuantity,
                     Recipe, Tag, User)
from .utils import check_user_and_request

USER_SERIALIZER_FIELDS = (
    'id',
    'email',
    'username',
    'first_name',
    'last_name',
    'is_subscribed',
)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag


class UserSerializer(DjoserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = USER_SERIALIZER_FIELDS
        model = User
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        return Follow.objects.filter(
            follower=request.user, author=obj
        ).exists()


class RecipesAndFavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = fields


class SubsciptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(default=True)
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        fields = (
            *USER_SERIALIZER_FIELDS,
            'recipes',
            'recipes_count',
        )
        model = User
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        follower = self.context.get('request').user
        author = self.instance
        if follower == author:
            raise serializers.ValidationError(
                detail={'errors': 'Вы не можете подписаться на самого себя'},
                code=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(follower=follower, author=author).exists():
            raise serializers.ValidationError(
                detail={'errors': 'Вы уже подписаны на этого пользователя'},
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipesAndFavoriteSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        read_only=True,
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientQuantity
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        error_messages={'does_not_exist': 'Указанного тега не существует'}
    )
    author = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipes'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_author(self, obj):
        return UserSerializer(
            get_object_or_404(User, id=obj.author.id),
            context=self.context
        ).data

    def get_is_favorited(self, obj):
        check_result, user = check_user_and_request(
            self.context.get('request')
        )
        if check_result:
            return Favorite.objects.filter(
                user=user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        check_result, user = check_user_and_request(
            self.context.get('request')
        )
        if check_result:
            return Cart.objects.filter(user=user, recipe=obj).exists()
        return False
