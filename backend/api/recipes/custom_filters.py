from django_filters import CharFilter, FilterSet, ModelMultipleChoiceFilter

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр рецептов."""

    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = CharFilter(method='get_favorite')
    is_in_shopping_cart = CharFilter(method='get_is_in_shopping_cart')

    def get_favorite(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favorite_recipes__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                shopping_carts__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
