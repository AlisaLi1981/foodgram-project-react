from django.contrib import admin
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'amount', 'recipe',)
    search_fields = ('recipe__name', 'ingredient__name',)
    list_filter = ('ingredient__name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name', 'slug',)
    list_editable = ('color',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'in_favorites',)
    readonly_fields = ('in_favorites',)
    list_filter = ('author', 'name', 'tags',)
    inlines = (RecipeIngredientInline,)

    def in_favorites(self, obj):
        return obj.favorite.count()

    in_favorites.short_description = 'Добавлений в избранное'


class ShoppingCartAdmin(admin.ModelAdmin):
    recipe__name = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)
    list_filter = ('user__username', 'recipe__name',)


class FavoriteAdmin(admin.ModelAdmin):
    recipe__name = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)
    list_filter = ('user__username', 'recipe__name',)


admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Tag, TagAdmin)
