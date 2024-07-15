[![Main Foodgram workflow](https://github.com/P1nk-L0rD/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/P1nk-L0rD/foodgram/actions/workflows/main.yml)

# Foodgram

Try website: https://foodgram.ddns.net/

## Описание

Сайт, куда можно выкладывать рецепты еды.

Возможности сайта:

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
Python (Django Framework, Django Rest Framework, django-filter, djoser), , Nginx, Gunicorn, Docker, GitHub Actions

**Frontend**
Javascript, React, CSS и другие

## Deployment on remote server

1. Клонируйте репозиторий к себе на комьютер

```bash
git clone git@github.com:P1nk-L0rD/foodgram.git
```

2. Создайте папку foodgram на удаленном сервере

3. Перенесите в папку файл docker-compose.production.yml

4. Переименуйте .env.example -> .env, заполните его своими данными и положите в папку foodgram

5. Обновите конфигурацию nginx на сервере, добавьте код:

```bash
location / {
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:9080;
}
```

Вы можете сменить порт, однако важно сделать это и в файле docker-compose.production.yml nginx -> ports

6. Проверьте конфигурацию nginx и перезапустите его если все ок:

```bash
sudo nginx -t
sudo service nginx reload
```

7. Добавьте данные в Github Actions:

```bash
DOCKER_USERNAME - юзернейм от DockerHub аккаунта
DOCKER_PASSWORD -  пароль от DockerHub аккаунта
HOST - IP-адрес удаленного сервера
USER - имя пользователя на уделанном сервере
SSH_KEY - SSH-ключ для подключения к серверу
SSH_PASSPHRASE - пассфраза для подключения
TELEGRAM_TO - ваш telegram id
TELEGRAM_TOKEN - токен телеграм-бота, который пришлет вам уведомление
```

8. Запушьте проект на GitHub или запустите Github Action

## Заполнение БД ингредиентами и тегами

To create ingredients:

```python
python manage.py fill_db_with_ingredients
# With Docker:
sudo docker compose -f docker-compose.production.yml exec backend python manage.py fill_db_with_ingredients
```

needed: ingredients.json in data folder

To create tags:

```python
python manage.py fill_db_with_tags
# With Docker:
sudo docker compose -f docker-compose.production.yml exec backend python manage.py fill_db_with_tags
```

needed: tags.json in data folder

## Authors

Yandex + [Me](https://github.com/P1nk-L0rD)