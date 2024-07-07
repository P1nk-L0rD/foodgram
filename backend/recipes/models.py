from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import MAX_NAME_LENGTH

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name="Название",
    )

    measurement_unit = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name="Единица измерения",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name="Название",
    )

    slug = models.SlugField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        verbose_name="Слаг",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Recipe(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name="Название",
    )

    description = models.TextField(
        verbose_name="Описание",
    )

    cooking_time = models.IntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1440),
        ],
    )

    pub_date = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        editable=False,
        verbose_name="Дата публикации",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
    )

    image = models.ImageField(
        verbose_name="Изображение",
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredients",
        blank=False,
        verbose_name="Ингредиенты",
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )

    amount = models.IntegerField(
        verbose_name="Количество",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100_000),
        ],
    )


class FavoriteCartMixin(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    pub_date = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        editable=False,
        verbose_name="Дата добавления",
    )

    class Meta:
        abstract = True


class Favorite(FavoriteCartMixin):

    class Meta:
        ordering = ["-pub_date"]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_favorite",
            ),
        ]


class ShoppingCart(FavoriteCartMixin):
    class Meta:
        ordering = ["-pub_date"]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_shopping_cart",
            ),
        ]
