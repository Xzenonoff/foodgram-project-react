# Generated by Django 4.1.7 on 2023-04-05 21:05

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "username",
                    models.CharField(
                        max_length=150, unique=True, verbose_name="Пользователь"
                    ),
                ),
                ("first_name", models.CharField(max_length=150, verbose_name="Имя")),
                ("last_name", models.CharField(max_length=150, verbose_name="Фамилия")),
            ],
            options={
                "verbose_name": "пользователь",
                "verbose_name_plural": "пользователи",
                "ordering": ("username",),
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Cart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "корзина",
                "verbose_name_plural": "корзина",
                "ordering": ("user",),
            },
        ),
        migrations.CreateModel(
            name="Favorite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "избранное",
                "verbose_name_plural": "избранное",
                "ordering": ("user",),
            },
        ),
        migrations.CreateModel(
            name="Follow",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "подписка на пользователя",
                "verbose_name_plural": "подписки на пользователей",
                "ordering": ("author",),
            },
        ),
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=200, unique=True, verbose_name="название"
                    ),
                ),
                (
                    "measurement_unit",
                    models.CharField(max_length=200, verbose_name="ед. измерения"),
                ),
            ],
            options={
                "verbose_name": "ингредиент",
                "verbose_name_plural": "ингредиенты",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="IngredientQuantity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                1, message="Мин. количество ингредиентов 1"
                            )
                        ],
                        verbose_name="кол-во",
                    ),
                ),
                (
                    "ingredient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ingredients",
                        to="api.ingredient",
                        verbose_name="ингредиент",
                    ),
                ),
            ],
            options={
                "verbose_name": "кол-во ингредиентов",
                "verbose_name_plural": "кол-во ингредиентов",
                "ordering": ("recipe",),
            },
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(max_length=200, unique=True, verbose_name="слаг"),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=200, unique=True, verbose_name="название"
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        max_length=7,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                                message="incorrect hex",
                            )
                        ],
                        verbose_name="цвет",
                    ),
                ),
            ],
            options={
                "verbose_name": "тэг",
                "verbose_name_plural": "тэги",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, verbose_name="название")),
                ("image", models.ImageField(upload_to="", verbose_name="фото")),
                ("text", models.TextField(verbose_name="сам рецепт")),
                (
                    "cooking_time",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                1, message="Минимальное время приготовления - 1 мин."
                            )
                        ],
                        verbose_name="время приготовления",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipes",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="автор",
                    ),
                ),
                (
                    "ingredients",
                    models.ManyToManyField(
                        through="api.IngredientQuantity",
                        to="api.ingredient",
                        verbose_name="ингредиенты",
                    ),
                ),
                ("tags", models.ManyToManyField(to="api.tag", verbose_name="тэги")),
            ],
            options={
                "verbose_name": "рецепт",
                "verbose_name_plural": "рецепты",
                "ordering": ("name",),
            },
        ),
        migrations.AddField(
            model_name="ingredientquantity",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipes",
                to="api.recipe",
                verbose_name="рецепт",
            ),
        ),
        migrations.AddConstraint(
            model_name="ingredient",
            constraint=models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="name_measurement_unit_constraint",
            ),
        ),
        migrations.AddField(
            model_name="follow",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="following",
                to=settings.AUTH_USER_MODEL,
                verbose_name="автор",
            ),
        ),
        migrations.AddField(
            model_name="follow",
            name="follower",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="follower",
                to=settings.AUTH_USER_MODEL,
                verbose_name="подписчик",
            ),
        ),
        migrations.AddField(
            model_name="favorite",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorite",
                to="api.recipe",
                verbose_name="рецепт",
            ),
        ),
        migrations.AddField(
            model_name="favorite",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="пользователь",
            ),
        ),
        migrations.AddField(
            model_name="cart",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipes_cart",
                to="api.recipe",
                verbose_name="рецепт",
            ),
        ),
        migrations.AddField(
            model_name="cart",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="пользователь",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
        migrations.AddConstraint(
            model_name="recipe",
            constraint=models.UniqueConstraint(
                fields=("name", "cooking_time"), name="name_cooking_time_constraint"
            ),
        ),
        migrations.AddConstraint(
            model_name="recipe",
            constraint=models.UniqueConstraint(
                fields=("name", "image"), name="name_image_constraint"
            ),
        ),
        migrations.AddConstraint(
            model_name="recipe",
            constraint=models.UniqueConstraint(
                fields=("name", "text"), name="name_text_constraint"
            ),
        ),
        migrations.AddConstraint(
            model_name="ingredientquantity",
            constraint=models.UniqueConstraint(
                fields=("recipe", "ingredient"), name="recipe_ingredient_constraint"
            ),
        ),
        migrations.AddConstraint(
            model_name="follow",
            constraint=models.UniqueConstraint(
                fields=("follower", "author"), name="follower_author_constraint"
            ),
        ),
        migrations.AddConstraint(
            model_name="favorite",
            constraint=models.UniqueConstraint(
                fields=("recipe", "user"), name="recipe_user_constraint"
            ),
        ),
        migrations.AddConstraint(
            model_name="cart",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="user_recipe_constraint"
            ),
        ),
    ]
