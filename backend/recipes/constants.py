from enum import Enum


class RecipesConstants(Enum):
    RECIPE_NAME_MAX_LENGTH = 200
    MIN_COOKING_TIME = 1
    MAX_COOKING_TIME = 32767
    PAGE_SIZE = 6


class TagsConstants(Enum):
    TAG_NAME_MAX_LENGTH = 200
    SLUG_MAX_LENGTH = 200
    COLOR_MAX_LENGTH = 7


class IngredientConstants(Enum):
    INGREDIENT_NAME_MAX_LENGTH = 200
    MEASUREMENT_UNIT_MAX_LENGTH = 200
    MIN_AMOUNT = 1

