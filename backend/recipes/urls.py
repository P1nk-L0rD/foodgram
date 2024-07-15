from django.urls import path

from api.recipes.views import short_link_handler

urlpatterns = [
    path('<slug:slug>/', short_link_handler, name='short_link_handler'),
]
