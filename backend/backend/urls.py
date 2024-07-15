from django.contrib import admin
from django.urls import include, path

from api.recipes.views import short_link_handler

urlpatterns = [
    path('api/', include('api.urls')),
    path('s/<slug:slug>', short_link_handler, name='short_link_handler'),
    path('admin/', admin.site.urls),
]
