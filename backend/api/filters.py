from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user_id = self.request.user.id
        if value and user_id:
            return queryset.filter(shopping_cart__user_id=user_id)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        user_id = self.request.user.id
        if value and user_id:
            return queryset.filter(favorite__user_id=user_id)
        return queryset
