from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from recipes.models import Ingredient, Recipe, Tag
from .serializers import (
    IngredientSerializer, RecipeSerializer, TagSerializer
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'ingredient_list'
    )

    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def get_serializer_class(self):
    #     if self.action in ('create',):
    #         return RecipeCreateSerializer
    #     return super().get_serializer_class()
