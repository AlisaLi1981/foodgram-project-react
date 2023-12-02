from djoser.views import UserViewSet
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscriptions, User
from .serializers import (
    FavoriteSerializer, IngredientSerializer, RecipeSerializer,
    TagSerializer, ShoppingCartSerializer, SubscriptionsSerializer,
    CustomUserSerializer
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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if (self.request.method in permissions.SAFE_METHODS
                and self.request.user.is_authenticated):
            return CustomUserSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post', 'delete'])
    def subscribe_to_author(self, request, pk=None):
        if request.method == 'POST':
            recipe = self.get_object()
            author = recipe.author
            subscription = Subscriptions.objects.create(
                user=request.user, author=author)
            subscription.save()
            serializer = SubscriptionsSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            recipe = self.get_object()
            author = recipe.author
            subscription = Subscriptions.objects.filter(
                user=request.user, author=author).first()
            if subscription:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
