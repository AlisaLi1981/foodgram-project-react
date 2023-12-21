from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User

from .constants import RecipesConstants, TagsConstants, IngredientConstants


class Tag(models.Model):
    name = models.CharField(
        'Тег', max_length=TagsConstants.TAG_NAME_MAX_LENGTH.value,
        unique=True
    )
    color = ColorField(
        'Цвет шрифта',
        max_length=TagsConstants.COLOR_MAX_LENGTH.value,
        unique=True
    )
    slug = models.SlugField(
        max_length=TagsConstants.SLUG_MAX_LENGTH.value,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Допустимы буквы, цифры, подчеркивания и дефисы.',
                code='invalid_slug'
            ),
        ],
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Наименование',
        max_length=IngredientConstants.INGREDIENT_NAME_MAX_LENGTH.value
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=IngredientConstants.MEASUREMENT_UNIT_MAX_LENGTH.value
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )

    name = models.CharField(
        'Название рецепта',
        max_length=RecipesConstants.RECIPE_NAME_MAX_LENGTH.value
    )

    image = models.ImageField(
        verbose_name='Изображение', upload_to='recipes/images/'
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
            RecipesConstants.MIN_COOKING_TIME.value,
            message=(
                f'Время приготовления должно быть не менее'
                f'{RecipesConstants.MIN_COOKING_TIME.value} минуты!'
            ))],
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
            IngredientConstants.MIN_AMOUNT.value,
            message=(f'Количество продукта должно быть не менее'
                     f'{IngredientConstants.MIN_AMOUNT.value}!'))],
    )

    class Meta:
        verbose_name = 'Ингредиентов в рецепте'
        verbose_name_plural = 'Ингредиентов в рецепте'
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


class FavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class ShoppingCart(FavoriteShoppingCart):

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'

    def __str__(self):
        return (f'Рецепт {self.recipe.name} добавлен в список покупок')


class Favorite(FavoriteShoppingCart):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorite'

    def __str__(self):
        return f'Рецепт {self.recipe.name} добавлен в Избранное'
