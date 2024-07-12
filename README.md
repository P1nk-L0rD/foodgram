
# Foodgram

## Описание

Сайт, куда можно вылкадывать рецепты еды.

Возможности сайта:

Возможности:

* Регистрация
* Создание/редактирование/удаление своих рецептов
* Создание коротких ссылок на рецепты
* Создание и добавление ингредиентов (для админов)
* Создание и добавление тегов (для админов)
* Подписки на других пользователей
* Лента подписок (рецепты авторов, на которых вы подписаны)
* Добавление рецептов в избранное и в список покупок
* Возможность скачать список ингредиентов, необходимых для готовки
* Админ-панель с большим функционалом

## Tech stack

**Backend**
Python (Django Framework, Django Rest Framework)

**Frontend**
Javascript, React, CSS и другие

## Deployment

Переименуйте .env.example -> .env
Заполните своими данными

## Заполнение БД ингредиентами и тегами

To create ingredients:

```python
python manage.py fill_db_with_ingredients
```

needed: ingredients.json in data folder

To create tags:

```python
python manage.py fill_db_with_tags
```

needed: tags.json in data folder

## Authors

Yandex + [me](https://github.com/P1nk-L0rD)