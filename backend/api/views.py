from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscriptions, User

from .filters import IngredientFilter, RecipeFilter
from .paginators import CustomPagination
from .permissions import IsAuthenticatedAndAuthor
from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeGetSerializer,
                          RecipePostSerializer, ShoppingCartSerializer,
                          SubscriptionsGetSerializer,
                          SubscriptionsPostSerializer, TagSerializer)
from .utils import generate_shopping_list


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    pagination_class = CustomPagination
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeGetSerializer
        return RecipePostSerializer

    def get_permissions(self):
        if self.action in ('partial_update', 'destroy'):
            return (IsAuthenticatedAndAuthor(),)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteSerializer(
            data={'user': user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        get_object_or_404(
            Favorite,
            user=request.user.id,
            recipe=get_object_or_404(Recipe, pk=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = ShoppingCartSerializer(
            data={'user': user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        get_object_or_404(
            ShoppingCart,
            user=request.user.id,
            recipe=get_object_or_404(Recipe, pk=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user
        cart_items = ShoppingCart.objects.filter(user=user).order_by(
            'recipe__recipes_ingredient__ingredient__name')
        ingredients_dict = {}

        for cart_item in cart_items:
            recipe_ingredients = RecipeIngredient.objects.filter(
                recipe=cart_item.recipe
            )
            for recipe_ingredient in recipe_ingredients:
                ingredient_name = recipe_ingredient.ingredient.name
                ingredient_quantity = recipe_ingredient.amount
                ingredient_unit = recipe_ingredient.ingredient.measurement_unit

                if ingredient_name in ingredients_dict:
                    ingredients_dict[
                        ingredient_name]['quantity'] += ingredient_quantity
                else:
                    ingredients_dict[ingredient_name] = {
                        'quantity': ingredient_quantity,
                        'unit': ingredient_unit
                    }

        shopping_list_text = generate_shopping_list(ingredients_dict)

        response = HttpResponse(content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        response.write(shopping_list_text)

        return response


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'delete']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if (self.request.method in permissions.SAFE_METHODS
                and self.request.user.is_authenticated):
            return CustomUserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in [
            'subscribe', 'subscriptions', 'destroy', 'me'
        ]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=['post'])
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        serializer = SubscriptionsPostSerializer(
            data={'user': user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Subscriptions.objects.create(user=user, author=author)
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        subscription = get_object_or_404(
            Subscriptions, user=request.user, author__pk=id)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], pagination_class=CustomPagination)
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsGetSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
