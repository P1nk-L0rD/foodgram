import json
from typing import Any

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Заполнение бд ингредиентами"

    def handle(self, *args: Any, **options: Any) -> str:
        path = "data/ingredients.json"

        with open(path, 'r', encoding="utf-8") as file:
            text = file.read()

        ingridients = json.loads(text)
        objects = [Ingredient(**ingridient) for ingridient in ingridients]
        Ingredient.objects.bulk_create(objects)
        return "Created successfully"
