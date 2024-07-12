from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (MAX_AMOUNT, MAX_COOKING_TIME, MAX_DISPLAY_LEN,
                        MAX_NAME_LEN, MAX_TEXT_LEN, MIN_AMOUNT,
                        MIN_COOKING_TIME)

User = get_user_model()


class BaseModel(models.Model):

    class Meta:
        abstract = True

    def __str__(self):
        return self.name[:MAX_DISPLAY_LEN]


class Tag(BaseModel):
    """Модель тега."""

    name = models.CharField(
        max_length=MAX_NAME_LEN,
        verbose_name="Название",
    )

    slug = models.SlugField(
        max_length=MAX_NAME_LEN,
        unique=True,
        verbose_name="Слаг",
    )

    class Meta:
        ordering = ('id',)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        default_related_name = "tag"


class Ingredient(BaseModel):
    """Модель ингредиента."""

    name = models.CharField(
        max_length=MAX_NAME_LEN,
        verbose_name="Название",
    )

    measurement_unit = models.CharField(
        max_length=MAX_NAME_LEN,
        verbose_name="Единица измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        default_related_name = 'ingredient'
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            ),
        ]


class Recipe(BaseModel):
    """Модель рецептов."""

    name = models.CharField(
        max_length=MAX_NAME_LEN,
        verbose_name="Название",
    )

    text = models.TextField(
        verbose_name="Текст",
        max_length=MAX_TEXT_LEN,
    )

    cooking_time = models.IntegerField(
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME),
        ],
        verbose_name="Время приготовления",
    )

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        related_name="recipes",
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        related_name="recipes",
    )

    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="recipes/",
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name="Ингредиенты",
        related_name="recipes",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)


class RecipeIngredient(models.Model):
    """Модель связи ингредиентов с рецептами."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient_list',
    )

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient',
    )

    amount = models.IntegerField(
        verbose_name="Количество",
        validators=[
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_AMOUNT),
        ],
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name = 'Ингредиенты рецепта'
        ordering = ('id',)

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'


class FavoriteCartMixin(models.Model):
    """Миксин для избранного и корзины."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        ordering = ("id",)

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class Favorite(FavoriteCartMixin):
    """Модель избранного."""

    class Meta(FavoriteCartMixin.Meta):
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        default_related_name = "favorite_recipes"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_favorite_recipe",
            ),
        ]


class ShoppingCart(FavoriteCartMixin):
    """Модель корзины."""

    class Meta(FavoriteCartMixin.Meta):
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        default_related_name = "shopping_carts"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_shopping_cart",
            ),
        ]
