from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

MAX_LENGTH_150 = 150
MAX_LENGTH_200 = 200
MIN_VALUE_1 = 1


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(
        'Пользователь',
        max_length=MAX_LENGTH_150,
        unique=True)
    first_name = models.CharField('Имя', max_length=MAX_LENGTH_150)
    last_name = models.CharField('Фамилия', max_length=MAX_LENGTH_150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Tag(models.Model):
    slug = models.SlugField('слаг', unique=True, max_length=MAX_LENGTH_200)
    name = models.CharField('название', max_length=MAX_LENGTH_200, unique=True)
    color = models.CharField(
        'цвет',
        max_length=7,
        unique=True,
        validators=[RegexValidator(
            r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
            message='incorrect hex'
        )],)

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('название', max_length=MAX_LENGTH_200, unique=True)
    measurement_unit = models.CharField(
        'ед. измерения',
        max_length=MAX_LENGTH_200
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name_measurement_unit_constraint')
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField('название', max_length=50)
    image = models.ImageField('фото')
    text = models.TextField('сам рецепт')
    cooking_time = models.PositiveSmallIntegerField(
        'время приготовления',
        validators=(
            MinValueValidator(
                MIN_VALUE_1,
                message=f'Минимальное время приготовления - {MIN_VALUE_1} мин.'
            ),
        ),
    )
    tags = models.ManyToManyField(Tag, verbose_name='тэги')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='ингредиенты',
        through='IngredientQuantity',
        through_fields=('recipe', 'ingredient'),
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'cooking_time'],
                name='name_cooking_time_constraint'
            ),
            models.UniqueConstraint(
                fields=['name', 'image'],
                name='name_image_constraint'
            ),
            models.UniqueConstraint(
                fields=['name', 'text'],
                name='name_text_constraint'
            ),
        ]

    def __str__(self):
        return self.name


class IngredientQuantity(models.Model):
    amount = models.PositiveSmallIntegerField(
        'кол-во',
        validators=(
            MinValueValidator(
                MIN_VALUE_1,
                message=f'Мин. количество ингредиентов {MIN_VALUE_1}'
            ),
        ),
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        related_name='recipes'
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'кол-во ингредиентов'
        verbose_name_plural = 'кол-во ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='recipe_ingredient_constraint')
        ]

    def __str__(self):
        return f'Для {self.recipe} требуется {self.amount} {self.ingredient} '


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        on_delete=models.CASCADE,
        related_name='following'
    )
    follower = models.ForeignKey(
        User,
        verbose_name='подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )

    class Meta:
        verbose_name = 'подписка на пользователя'
        verbose_name_plural = 'подписки на пользователей'
        ordering = ('author',)
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'author'],
                name='follower_author_constraint'
            )
        ]

    def __str__(self):
        return f'{self.follower} подписан на {self.author}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        related_name='favorite'
    )
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='recipe_user_constraint'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном {self.user}'


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        related_name='recipes_cart',
    )

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'корзина'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_recipe_constraint'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в корзине {self.user}'
