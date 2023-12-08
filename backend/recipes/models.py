from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, RegexValidator
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
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Допустимы буквы, цифры, подчеркивания и дефисы.',
                code='invalid_slug'
            ),
        ],
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

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
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
        Ingredient, related_name='recipes',
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )

    tags = models.ManyToManyField(
        Tag, related_name='recipes',
        verbose_name='Теги'
    )

    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(
            1, message='Время приготовления должно быть не менее 1 минуты!')],
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipes_ingredients',
        on_delete=models.CASCADE)

    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipes_ingredients',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )

    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(
            1, message='Количество продукта должно быть не менее 1!')],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient'
            )
        ]

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
