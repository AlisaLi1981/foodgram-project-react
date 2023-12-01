from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscriptions
from .serializers import (
    FavoriteSerializer, IngredientSerializer, RecipeSerializer,
    TagSerializer, ShoppingCartSerializer, SubscriptionsSerializer
)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer = IngredientSerializer


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    @action(detail=True, methods=['post'])
    def add_to_favorite(self, request, pk=None):
        recipe = self.get_object()
        favorite = Favorite(user=request.user, recipe=recipe)
        favorite.save()
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_to_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        cart_item = ShoppingCart(user=request.user, recipe=recipe)
        cart_item.save()
        serializer = ShoppingCartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def subscribe_to_author(self, request, pk=None):
        recipe = self.get_object()
        author = recipe.author
        subscription = Subscriptions(user=request.user, author=author)
        subscription.save()
        serializer = SubscriptionsSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
