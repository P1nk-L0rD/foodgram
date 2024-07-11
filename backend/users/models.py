from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .constants import MAX_NAME_LEN, MAX_USERNAME_LEN
from .custom_validators import validate_username


class User(AbstractUser):
    """Модель пользователя"""

    REQUIRED_FIELDS = (
        "username", "first_name", "last_name"
    )
    USERNAME_FIELD = "email"

    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        max_length=MAX_NAME_LEN,
        unique=True,
    )

    username = models.CharField(
        verbose_name="Имя пользователя",
        max_length=MAX_USERNAME_LEN,
        unique=True,
        validators=[UnicodeUsernameValidator(), validate_username],
        error_messages={
            "unique": "Это имя пользователя уже занято!",
        }
    )

    first_name = models.CharField(
        verbose_name="Имя",
        max_length=MAX_NAME_LEN,
    )

    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=MAX_NAME_LEN,
    )

    avatar = models.ImageField(
        verbose_name="Фотография",
        blank=True,
        null=True,
        default=None,
        upload_to="avatars",
    )

    class Meta:
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):
    """Модель подписок"""

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='subscribers',
    )

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='author',
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription',
            ),
        ]

    def __str__(self):
        return f'Подписка {self.user} на {self.author}'
