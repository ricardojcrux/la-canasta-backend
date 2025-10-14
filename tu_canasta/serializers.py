from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .models import Product, ShoppingList, ShoppingListItem, User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'password',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        if password:
            validated_data['password'] = make_password(password)
        else:
            validated_data.pop('password', None)
        return super().update(instance, validated_data)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'sku',
            'name',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShoppingListItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_detail = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = ShoppingListItem
        fields = [
            'id',
            'product',
            'product_detail',
            'quantity',
            'added_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'product_detail', 'added_at', 'updated_at']


class ShoppingListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    items = ShoppingListItemSerializer(many=True, read_only=True)

    class Meta:
        model = ShoppingList
        fields = [
            'id',
            'user',
            'items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'items', 'created_at', 'updated_at']
