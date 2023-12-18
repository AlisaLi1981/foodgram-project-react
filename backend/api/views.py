from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfgen import canvas
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscriptions, User

from .filters import IngredientFilter, RecipeFilter
from .paginators import CustomPagination
from .permissions import AuthorOrReadOnly
from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeGetSerializer,
                          RecipePostSerializer, ShoppingCartSerializer,
                          SubscriptionsGetSerializer,
                          SubscriptionsPostSerializer, TagSerializer)


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

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeGetSerializer
        return RecipePostSerializer

    def get_permissions(self):
        if self.action in [
            'download_shopping_cart'
        ] or self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        elif self.request.method == 'DELETE' or self.request.method == 'PATCH':
            return [AuthorOrReadOnly()]
        else:
            return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {'detail': 'Рецепт не существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FavoriteSerializer(
                data={'user': user.id, 'recipe': recipe.id},
                context={'request': request}
            )
            if serializer.is_valid(raise_exception=True):
                Favorite.objects.create(user=user, recipe=recipe)
                return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=pk)
            serializer = FavoriteSerializer(
                data={'user': user.id, 'recipe': recipe.id},
                context={'request': request}
            )
            if serializer.is_valid(raise_exception=True):
                Favorite.objects.get(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {'detail': 'Рецепт не существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = ShoppingCartSerializer(
                data={'user': user.id, 'recipe': recipe.id},
                context={'request': request}
            )
            if serializer.is_valid(raise_exception=True):
                ShoppingCart.objects.create(user=user, recipe=recipe)
                return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=pk)
            serializer = ShoppingCartSerializer(
                data={'user': user.id, 'recipe': recipe.id},
                context={'request': request}
            )
            if serializer.is_valid(raise_exception=True):
                ShoppingCart.objects.get(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user
        cart_items = ShoppingCart.objects.filter(user=user)
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
                    ingredients_dict[ingredient_name]['quantity'] += ingredient_quantity
                else:
                    ingredients_dict[ingredient_name] = {
                        'quantity': ingredient_quantity,
                        'unit': ingredient_unit
                    }

        file_content = ''
        for ingredient_name, details in ingredients_dict.items():
            quantity = details['quantity']
            unit = details['unit']
            file_content += f'{ingredient_name} ({unit}) - {quantity}\n'

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        response.write(file_content)

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
        if self.request.method == 'DELETE' or self.action in [
            'subscribe', 'subscriptions', 'me'
        ]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        serializer = SubscriptionsPostSerializer(
            data={'user': user.id, 'author': author.id},
            context={'request': request}
        )
        if request.method == 'POST':
            if serializer.is_valid(raise_exception=True):
                Subscriptions.objects.create(user=user, author=author)
                return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            try:
                subscription = Subscriptions.objects.get(
                    user=user, author=author)
            except Subscriptions.DoesNotExist:
                return Response(
                    {'detail': 'Подписка не существует!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if serializer.is_valid(raise_exception=True):
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        user = self.request.user
        authors = User.objects.filter(is_subscribed__user=user)
        paginator = CustomPagination()
        paginator.page_size = request.query_params.get('recipes_limit', 10)
        result_page = paginator.paginate_queryset(authors, request)
        serializer = SubscriptionsGetSerializer(
            result_page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)
