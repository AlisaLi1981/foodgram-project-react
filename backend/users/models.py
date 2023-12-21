from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import F, Q

from .constants import UserConstants


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=UserConstants.PERSONAL_DATA_MAX_LENGTH.value,
        verbose_name='Имя пользователя',
        unique=True,
        validators=[username_validator],
    )

    email = models.EmailField(
        max_length=UserConstants.EMAIL_MAX_LENGTH.value,
        verbose_name='Почта',
        unique=True
    )

    first_name = models.CharField(
        'Имя', max_length=UserConstants.PERSONAL_DATA_MAX_LENGTH.value
    )
    last_name = models.CharField(
        'Фамилия', max_length=UserConstants.PERSONAL_DATA_MAX_LENGTH.value
    )

    USERNAME_FIELD = UserConstants.USERNAME_FIELD_VALUE.value
    REQUIRED_FIELDS = UserConstants.REQUIRED_FIELDS_VALUE.value

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_subscription'),
            models.CheckConstraint(check=~Q(user=F('author')),
                                   name='no_autosubscribe')
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
