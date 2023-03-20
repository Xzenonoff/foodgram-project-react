from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Ingredient, Tag, User, Follow, Recipe, IngredientQuantity


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        return Follow.objects.filter(
            follower=request.user, author=obj
        ).exists()

    class Meta:
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        model = User


class CreateUserSerializator(serializers.ModelSerializer):

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        model = User
        extra_kwargs = {'password': {'write_only': True}}

    def to_representation(self, instance):
        reply = super().to_representation(instance)
        del reply["password"]
        return reply

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)


class RecipesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubsciptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(default=True)
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        model = Follow

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            recipes = obj.author.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.author.recipes.all()
        return RecipesSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        recipes_quantity = Recipe.objects.filter(author=obj.author).count()
        return recipes_quantity


class RecipeIngredientSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'amount', 'measurement_unit')

    def get_amount(self, obj):
        amount = list(IngredientQuantity.objects.filter(
            ingredient_id=obj.id
        ).values('amount'))[0].get('amount')
        return amount


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(many=True)

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
            #'is_favorited',
            #'is_in_shopping_cart',
        )

    def get_author(self, obj):
        return UserSerializer(get_object_or_404(User, id=obj.author.id)).data
