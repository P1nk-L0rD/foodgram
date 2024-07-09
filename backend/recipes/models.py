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

    surname = models.TextField(

    )

    measurement_unit = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name="Единица измерения",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self) -> str:
        return self.name


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

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name="Название",
    )

    text = models.TextField(
        verbose_name="Текст",
    )

    cooking_time = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1440),
        ],
        verbose_name="Время приготовления",
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
        related_name="recipes",
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        related_name="recipes",
    )

    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="recipes",
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredients",
        blank=False,
        verbose_name="Ингредиенты",
        related_name="recipes",
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self) -> str:
        return self.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
    )

    amount = models.IntegerField(
        verbose_name="Количество",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100_000),
        ],
    )


# class RecipeTags(models.Model):
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE,
#     )

#     tag = models.ForeignKey(
#         Tag,
#         on_delete=models.CASCADE,
#     )


class FavoriteCartMixin(models.Model):
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
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
    )

    class Meta:
        ordering = ["-pub_date"]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_favorite",
            ),
        ]


class ShoppingCart(FavoriteCartMixin):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
    )

    class Meta:
        ordering = ["-pub_date"]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_shopping_cart",
            ),
        ]
