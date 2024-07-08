from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name")
    search_fields = ('username', 'email', 'first_name')


# UserAdmin.fieldsets += (
#         ('Extra Fields', {'fields': ('userpic',)}),
#     )
