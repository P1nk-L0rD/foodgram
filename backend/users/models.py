from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .constants import MAX_NAME_LEN
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
        max_length=MAX_NAME_LEN,
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

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'author'],
                name='unique_subscription',
            ),
        ]

    # def save(self, *args, **kwargs):
    #     if self.user == self.subscriber:
    #         raise ValueError("Пользователь не может подписаться на себя")
    #     super().save(*args, **kwargs)
