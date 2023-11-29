from colorfield.fields import ColorField
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'Тег', max_length=200,
        unique=True
    )
    color = ColorField(
        'Цвет шрифта',
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        max_length=200,
        unique=True
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Наименование', max_length=200
    )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=200
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recpies',
        verbose_name='Автор рецепта',
    )

    name = models.CharField(
        'Название рецепта', max_length=200
    )

    image = models.ImageField(
        upload_to='recipes/images/',
        default=None
    )

    text = models.TextField('Описание')

    ingredients = models.ManyToManyField(
        Ingredient, related_name='recpies',
        verbose_name='Ингредиенты'
    )

    tags = models.ManyToManyField(
        Ingredient, related_name='recpies',
        verbose_name='Теги'
    )

    cooking_time = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorite',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'Рецепт {self.recipe.name} добавлен в Избранное'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipes_ingredients',
        on_delete=models.CASCADE)

    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipes_ingredients',
        on_delete=models.CASCADE
    )

    amount = models.PositiveSmallIntegerField(
        'Количество'
    )

    def __str__(self):
        return (
            f'{self.ingredient.name}'
            f' - {self.amount}({self.ingredient.measurement_unit})'
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    def __str__(self):
        return (f'Рецепт {self.recipe.name} добавлен в список покупок')
