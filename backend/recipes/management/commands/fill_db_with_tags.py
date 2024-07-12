import json

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = "Заполнение бд тегами"

    def handle(self, *args, **options) -> str:
        path = "data/tags.json"

        with open(path, 'r', encoding="utf-8") as file:
            text = file.read()

        ingridients = json.loads(text)
        objects = [Tag(**ingridient) for ingridient in ingridients]
        Tag.objects.bulk_create(objects)
        return "Created successfully"
