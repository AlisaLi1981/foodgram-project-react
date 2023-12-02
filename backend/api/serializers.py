from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscriptions, User


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'


class SubscriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions
        fields = '__all__'


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user is None or user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=user, author=obj).exists()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
#        extra_kwargs = {
#            'email': {'required': True},
#            'username': {'required': True},
#            'first_name': {'required': True},
#            'last_name': {'required': True},
#            'password': {'required': True},
#        }
