from django.contrib import admin
from django.contrib.admin import display

from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag

# class RecipeAdmin(admin.ModelAdmin):
#     list_display = ('name', 'id', 'author', 'added_in_favorites')
 #    readonly_fields = ('added_in_favorites',)
#    list_filter = ('author', 'name', 'tags',)
#
#    @display(description='Количество в избранных')
#    def added_in_favorites(self, obj):
#        return obj.favorite_recipe.count()


admin.site.register(Favorite)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
