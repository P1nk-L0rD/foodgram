from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .recipes.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                            short_link_handler)
from .users.views import UserViewSet

api_v1 = DefaultRouter()
api_v1.register(r'users', UserViewSet, basename='users')
api_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
api_v1.register(r'tags', TagViewSet, basename='tags')
api_v1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(api_v1.urls)),
    path('s/<slug:slug>', short_link_handler, name='short_link_handler'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
