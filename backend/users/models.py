from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True,
    )

    email = models.EmailField(
        max_length=254,
        verbose_name='Почта',
        unique=True
    )

    first_name = models.CharField(
        'Имя',
        max_length=150
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150
    )

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscriber')

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='is_subscribed')

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
