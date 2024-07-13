from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers

from api.users.fields import Base64ImageField
from api.users.serializers import UserSerializer
from recipes.constants import (MAX_AMOUNT, MAX_COOKING_TIME, MIN_AMOUNT,
                               MIN_COOKING_TIME)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription

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
        self.add_tags_and_ingredients(recipe, tags, ingredients)
        return recipe

    def validate(self, attrs):
        objects_to_validate = ('tags', 'ingredients')
        for object in objects_to_validate:
            objects = attrs.get(object)

            if not objects:
                raise serializers.ValidationError(f'Укажите {object}!')

            if isinstance(objects[0], OrderedDict):
                obj_set = {one_object['id'] for one_object in objects}
            else:
                obj_set = {tag for tag in objects}

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
        self.add_tags_and_ingredients(instance, tags, ingredients)

        return super().update(instance, validated_data)

    def add_tags_and_ingredients(self, recipe, tags, ingredients):
        for tag_id in tags:
            recipe.tags.add(tag_id)

        ingredient_list = []
        for ingredient in ingredients:
            pk = ingredient.get('id')
            amount = ingredient.get('amount')
            ingredient_list.append(
                RecipeIngredient(recipe=recipe, ingredient=pk, amount=amount)
            )

        RecipeIngredient.objects.bulk_create(ingredient_list)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance=instance,
            context={'request': request}
        ).data


class SubscriptionSerializer(UserSerializer):
    """Сериалайзер для получения результата подписки."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(UserSerializer.Meta):
        fields = (*UserSerializer.Meta.fields, 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True).data


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
