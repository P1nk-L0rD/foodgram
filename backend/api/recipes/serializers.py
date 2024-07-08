
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, Tag, Recipe, RecipeIngredients
from rest_framework import serializers

from api.users.serializers import UserSerializer, Base64ImageField


User = get_user_model()


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для короткого отображения рецептов."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerialiser(serializers.ModelSerializer):
    # ingredient = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = RecipeIngredients
        fields = ('id', )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    # tags = serializers.PrimaryKeyRelatedField(
    #     many=True, queryset=Tag.objects.all()
    # )
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerialiser(read_only=True, many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image',
            'text', 'cooking_time',
        )

    def create(self, validated_data):
        recipe = Recipe.objects.create(**validated_data)

        if "ingredients" not in self.initial_data:
            raise serializers.ValidationError("Укажите ингредиенты!")

        ingredients = self.initial_data.get('ingredients')
        for ingredient in ingredients:
            pk = ingredient.get('id')
            amount = ingredient.get('amount')
            ingredient = get_object_or_404(Ingredient, pk=pk)

            RecipeIngredients.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )

        # tags = self.initial_data.get('tags')
        # Recipe.objects.filter(pk=recipe.pk).update(tags=tags)

        return recipe


# class SubscriptionSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Subscription
#         fields = ()
