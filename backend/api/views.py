from djoser.views import UserViewSet
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscriptions, User
from .serializers import (
    FavoriteSerializer, IngredientSerializer, RecipeGetSerializer,
    RecipePostSerializer,
    TagSerializer, ShoppingCartSerializer, SubscriptionsGetSerializer,
    SubscriptionsPostSerializer, CustomUserSerializer
)
from .permissions import AdminOrReadOnly, AuthorOrReadOnly


class IngredientViewSet(ReadOnlyModelViewSet):
    permission_classes = [AdminOrReadOnly, ]
    queryset = Ingredient.objects.all()
    serializer = IngredientSerializer


class TagViewSet(ReadOnlyModelViewSet):
    permission_classes = [AdminOrReadOnly, ]
    queryset = Tag.objects.all()
    serializer = TagSerializer


class RecipeViewSet(ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = Recipe.objects.all()
    permission_classes = [AuthorOrReadOnly, ]

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticatedOrReadOnly],)
    def add_to_favorite(self, request, pk=None):
        recipe = self.get_object()
        favorite = Favorite(user=request.user, recipe=recipe)
        favorite.save()
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticatedOrReadOnly],)
    def add_to_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        cart_item = ShoppingCart(user=request.user, recipe=recipe)
        cart_item.save()
        serializer = ShoppingCartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'],
            permission_classes=[permissions.IsAuthenticatedOrReadOnly],)
    def remove_from_favorite(self, request, pk=None):
        recipe = self.get_object()
        try:
            favorite = Favorite.objects.get(user=request.user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['delete'],
            permission_classes=[permissions.IsAuthenticatedOrReadOnly],)
    def remove_from_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        try:
            cart_item = ShoppingCart.objects.get(user=request.user, recipe=recipe)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ShoppingCart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = PageNumberPagination

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
            serializer = SubscriptionsPostSerializer(subscription)
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

    @action(detail=True, methods=['get'])
    def list_subscriptions(self, request):
        user = self.get_object()
        subscriptions = Subscriptions.objects.filter(user=user)
        serializer = SubscriptionsGetSerializer(subscriptions, many=True)
        return Response(serializer.data)
