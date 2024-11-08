from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .custom_filters import IngredientFilter, RecipeFilter
from .custom_pagination import CustomPagination
from .serializers import (FavoriteCreateSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShoppingCartCreateSerializer, SubscriptionSerializer,
                          TagSerializer)
from api.recipes import custom_permissions
from api.recipes.constants import SCALE_OF_NOTATION
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription


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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'ingredient_list'
    )

    permission_classes = (custom_permissions.IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('^name')
    filterset_class = RecipeFilter
    filterset_fields = ('name', 'author')
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    def favorite_cart_mixin(self, request, pk, model, serializer, name):
        """Функци для корзины/избранного."""

        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        exist = model.objects.filter(
            user=user, recipe=recipe,
        ).exists()

        if request.method == 'POST':
            if exist:
                return Response(
                    {'errors': f"Рецепт уже в {name}!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = serializer(
                data={'user': request.user.id, 'recipe': pk},
                context={'request': request}
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not exist:
            return Response(
                {'errors': f"Рецепта нет в {name}!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        model.objects.filter(
            user=user, recipe=recipe
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='favorite',
    )
    def favorite(self, request, pk):
        """Функция для добавления/удаления избранных рецептов."""

        return self.favorite_cart_mixin(
            request, pk, Favorite, FavoriteCreateSerializer,
            'favorite'
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        """Функция для добавления/удаления списка покупок."""

        return self.favorite_cart_mixin(
            request, pk, ShoppingCart, ShoppingCartCreateSerializer,
            'shopping_cart'
        )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_carts__user=self.request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(sum=Sum('amount')).order_by(
            'ingredient__name'
        )

        answer_text = 'Список необходмых ингредиентов:\n\n'
        for ingredient in ingredients:
            name, unit, sum = ingredient.values()
            answer_text += f"{name}: {sum} {unit}\n"

        return HttpResponse(
            answer_text,
            content_type='text/plain',
            status=status.HTTP_200_OK
        )

    @action(
        methods=['GET'],
        detail=True,
        permission_classes=(permissions.AllowAny,),
        url_path='get-link',
    )
    def short_link(self, request, pk):
        """Генератор коротких ссылок формата /s/<slug>/."""
        link_part = reverse('short_link_handler', args=[hex(int(pk))])
        short_link = request.build_absolute_uri(link_part)
        return Response(
            {'short-link': short_link},
            status=status.HTTP_200_OK
        )


def short_link_handler(request, slug):
    """Приниматор коротких ссылок и переадрессатор на рецепт."""
    recipe_pk = int(slug, SCALE_OF_NOTATION)
    full_link = request.build_absolute_uri(f'/recipes/{recipe_pk}/')
    return redirect(full_link)


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для подписок."""

    queryset = Subscription.objects.select_related('author').prefetch_related(
        'recipes'
    )
    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)
