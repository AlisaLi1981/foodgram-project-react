from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from recipes.models import (Favorite, Ingredient, RecipeIngredient,
                            Recipe, ShoppingCart, Tag)
from users.models import Subscriptions, User


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже добавлен в избранное.')
        if not Recipe.objects.filter(pk=recipe.pk).exists():
            raise serializers.ValidationError('Указанный рецепт не существует.')

        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже добавлен в список покупок.')
        if not Recipe.objects.filter(pk=recipe.pk).exists():
            raise serializers.ValidationError('Указанный рецепт не существует.')

        return data


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user is None or request.user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=request.user, author=obj).exists()

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


class SubscriptionsPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscriptions
        fields = (
            'user',
            'author',
        )

    def to_representation(self, instance):
        return SubscriptionsGetSerializer(instance['author'], context={
            'request': self.context.get('request')
        }).data


class CustomUserCreateSerializer(UserCreateSerializer):

    def validate(self, attrs):
        username = attrs.get('username')
        if username == 'me':
            raise serializers.ValidationError({'username': 'Недопустимое значение для имени пользователя!'})
        return attrs

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


class RecipeGetSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientGetSerializer(many=True, source='recipes_ingredients', read_only=True)

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and user.favorite.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and user.shopping_cart.filter(recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )


class SubscriptionsGetSerializer(CustomUserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        subscriptions = Subscriptions.objects.filter(user=obj)
        authors = [subscription.author for subscription in subscriptions]
        recipes = Recipe.objects.filter(author__in=authors)
        return RecipeGetSerializer(recipes, many=True).data


class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=True)
    ingredients = RecipeIngredientPostSerializer(many=True, source='recipes_ingredients', required=True)
    cooking_time = serializers.IntegerField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )

    def validate_recipes_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("Ингредиенты обязательны.")
        ingredient_ids = [ingredient.get('id') for ingredient in value]
        if not Ingredient.objects.filter(id__in=ingredient_ids).exists():
            raise serializers.ValidationError("Один или несколько ингредиентов не существуют в базе данных.")
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError("Нельзя добавить один и тот же ингредиент дважды в один рецепт.")

        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError("Теги обязательны.")
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Нельзя добавить один и тот же тег дважды.")

        return value

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('recipes_ingredients')
        tags = validated_data.pop('tags')
        recipe = request.user.recipes.create(
            **validated_data
        )
        recipe.tags.set(tags)
        self._create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipes_ingredients')
    #    tags = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.tags.set(validated_data.get('tags', instance.tags.all()))
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self._create_ingredients(recipe=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeGetSerializer(instance, context=context).data

    def _create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    ingredient_id=ingredient['id'],
                    recipe=recipe,
                    amount=ingredient['amount'],
                )
                for ingredient in ingredients
            ]
        )
