from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from io import BytesIO
from reportlab.pdfgen import canvas
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import Subscriptions, User
from .serializers import (
    FavoriteSerializer, IngredientSerializer, RecipeGetSerializer,
    RecipePostSerializer,
    TagSerializer, ShoppingCartSerializer, SubscriptionsGetSerializer,
    SubscriptionsPostSerializer, CustomUserSerializer
)
from .permissions import AdminOrReadOnly, AuthorOrReadOnly
from .paginators import CustomPagination


class IngredientViewSet(ReadOnlyModelViewSet):
    # permission_classes = [AdminOrReadOnly, ]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(ReadOnlyModelViewSet):
    # permission_classes = [AdminOrReadOnly, ]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    pagination_class = CustomPagination
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeGetSerializer
        return RecipePostSerializer

    def get_permissions(self):
        if self.action in ['add_to_favorite', 'add_to_shopping_cart', 'download_shopping_cart']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['remove_from_favorite', 'remove_from_shopping_cart']:
            return [permissions.IsAuthenticated(), AuthorOrReadOnly()]
        else:
            return [permissions.IsAuthenticatedOrReadOnly(), AuthorOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], url_path='favorite')
    def add_to_favorite(self, request, pk=None):
        recipe = self.get_object()
        favorite = Favorite(user=request.user, recipe=recipe)
        favorite.save()
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='shopping_cart')
    def add_to_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        cart_item = ShoppingCart(user=request.user, recipe=recipe)
        cart_item.save()
        serializer = ShoppingCartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='favorite')
    def remove_from_favorite(self, request, pk=None):
        recipe = self.get_object()
        try:
            favorite = Favorite.objects.get(user=request.user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['delete'], url_path='shopping_cart')
    def remove_from_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        try:
            cart_item = ShoppingCart.objects.get(user=request.user, recipe=recipe)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ShoppingCart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user
        cart_items = ShoppingCart.objects.filter(user=user)
        ingredients_dict = {}
        for cart_item in cart_items:
            recipe_ingredients = RecipeIngredient.objects.filter(recipe=cart_item.recipe)
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

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.setTitle('Shopping List')
        for ingredient_name, details in ingredients_dict.items():
            quantity = details['quantity']
            unit = details['unit']
            pdf.drawString(100, 700, f"{ingredient_name} ({unit}) — {quantity}")

        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.pdf"'
        response.write(buffer.read())

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
            data={
                'user': user.id,
                'author': author.id
            },
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
            if serializer.is_valid(raise_exception=True):
                Subscriptions.objects.get(user=user, author=author).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        user = self.request.user
        authors = User.objects.filter(is_subscribed__user=user)
        serializer = SubscriptionsGetSerializer(authors, many=True, context={'request': request})
        return Response(serializer.data)
