from ..users.serializers import Base64ImageField, UserSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredients, Tag

User = get_user_model()


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Короткие рецепты (только id, name, image, time)."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerialiser(serializers.ModelSerializer):
    """Сериалайзер для ингредиентов рецептов."""

    class Meta:
        model = RecipeIngredients
        fields = ('id',)

    def list(self, request):
        print(request, self)

    def retrieve(self, request):
        print(request, self)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для получения рецептов."""

    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    # ingredients = IngredientRecipeSerialiser(read_only=True, many=True)
    ingredients = IngredientSerializer(read_only=True, many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image',
            'text', 'cooking_time',
        )

    def create(self, validated_data):
        recipe = Recipe.objects.create(**validated_data)

        objects = ('ingredients', 'tags')

        for object in objects:
            if object not in self.initial_data:
                raise serializers.ValidationError(f"Укажите {object}!")

        ingredients = self.initial_data.get('ingredients')
        for ingredient in ingredients:
            pk = ingredient.get('id')
            amount = ingredient.get('amount')
            ingredient = get_object_or_404(Ingredient, pk=pk)

            RecipeIngredients.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )

        tags = self.initial_data.get('tags')
        for tag_id in tags:
            tag = get_object_or_404(Tag, pk=tag_id)
            recipe.tags.add(tag)
        recipe.save()
        return recipe

    def to_representation(self, instance):

        # print(self, instance)
        print(instance.data)

        return super().to_representation(instance)


class RecipeCreateSerializer(RecipeSerializer):
    """Сериалайзер для создания рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        read_only=False,
        many=True,
        queryset=Tag.objects.all(),
    )

    class Meta(RecipeSerializer.Meta):
        ...

    # def create(self, validated_data):
    #     recipe = Recipe.objects.create(**validated_data)

    #     if "ingredients" not in self.initial_data:
    #         raise serializers.ValidationError("Укажите ингредиенты!")

    #     ingredients = self.initial_data.get('ingredients')
    #     for ingredient in ingredients:
    #         pk = ingredient.get('id')
    #         amount = ingredient.get('amount')
    #         ingredient = get_object_or_404(Ingredient, pk=pk)

    #         RecipeIngredients.objects.create(
    #             recipe=recipe, ingredient=ingredient, amount=amount
    #         )

    #     return recipe


class SubscriptionSerializer(UserSerializer):
    """Сериалайзер для подписок."""

    recipes = ShortRecipeSerializer(read_only=True, many=True)

    class Meta(UserSerializer.Meta):
        fields = (*UserSerializer.Meta.fields, "recipes")
