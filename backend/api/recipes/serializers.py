from collections import OrderedDict

from ..users.serializers import Base64ImageField, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator

from recipes.models import (
    Ingredient, Recipe, RecipeIngredient, Tag, Favorite, ShoppingCart
)
from users.models import Subscription
from recipes.constants import (
    MIN_AMOUNT, MAX_AMOUNT, MIN_COOKING_TIME, MAX_COOKING_TIME
)

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


class RecipeIngredientSerialiser(serializers.ModelSerializer):
    """Сериалайзер для ингредиентов рецептов."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerialiser(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_AMOUNT),
        ]
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для получения рецептов."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = RecipeIngredientSerialiser(
        read_only=True, many=True, source='ingredient_list')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(default=False)
    is_in_shopping_cart = serializers.SerializerMethodField(default=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image',
            'text', 'cooking_time', 'is_favorited', 'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        request = self.context['request']
        if not request or not request.user.is_authenticated:
            return False
        return request.user.favorite_recipes.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        if not request or not request.user.is_authenticated:
            return False
        return request.user.shopping_carts.filter(recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientCreateSerialiser(many=True, required=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME),
        ]
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image',
            'text', 'cooking_time',
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for tag_id in tags:
            recipe.tags.add(tag_id)
        recipe.save()

        for ingredient in ingredients:
            pk = ingredient.get('id')
            amount = ingredient.get('amount')
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=pk, amount=amount
            )

        return recipe

    def validate(self, attrs):
        objects_to_validate = ('tags', 'ingredients')
        for object in objects_to_validate:
            objects = attrs.get(object)

            if not objects:
                raise serializers.ValidationError(f'Укажите {object}!')

            if isinstance(objects[0], OrderedDict):
                obj_set = {object['id'] for object in objects}
            else:
                obj_set = objects

            if len(objects) != len(obj_set):
                raise serializers.ValidationError(
                    f'{object} не должны повторяться!'
                )

        return attrs

    def update(self, instance: Recipe, validated_data):
        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance.tags.clear()

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        for tag_id in tags:
            instance.tags.add(tag_id)
        instance.save()

        for ingredient in ingredients:
            pk = ingredient.get('id')
            amount = ingredient.get('amount')
            RecipeIngredient.objects.create(
                recipe=instance, ingredient=pk, amount=amount
            )

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance=instance,
            context={'request': request}
        ).data


class SubscriptionSerializer(UserSerializer):
    """Сериалайзер для результата подписки."""

    recipes = ShortRecipeSerializer(read_only=True, many=True)
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(UserSerializer.Meta):
        fields = (*UserSerializer.Meta.fields, 'recipes', 'recipes_count')


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания подписки."""

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscriptionSerializer(
            instance.author,
            context={'request': request}
        ).data


class FavoriteCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для добавление в избранное."""

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class ShoppingCartCreateSerializer(FavoriteCreateSerializer):
    """Сериалайзер для добавление в список покупок."""

    class Meta(FavoriteCreateSerializer.Meta):
        model = ShoppingCart
