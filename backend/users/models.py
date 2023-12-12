from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import F, Q


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True,
        validators=[username_validator],
    )

    email = models.EmailField(
        max_length=254,
        verbose_name='Почта',
        unique=True
    )

    first_name = models.CharField(
        'Имя', max_length=150
    )
    last_name = models.CharField(
        'Фамилия', max_length=150
    )

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
        related_name='is_subscribed',
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
