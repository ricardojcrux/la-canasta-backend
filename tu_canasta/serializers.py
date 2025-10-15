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
    shopping_list = serializers.PrimaryKeyRelatedField(
        queryset=ShoppingList.objects.none()
    )
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_detail = ProductSerializer(source='product', read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = ShoppingListItem
        fields = [
            'id',
            'shopping_list',
            'product',
            'product_detail',
            'quantity',
            'unit_price',
            'is_purchased',
            'total_price',
            'added_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'product_detail',
            'total_price',
            'added_at',
            'updated_at',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context.get('request_user')
        if user:
            self.fields['shopping_list'].queryset = ShoppingList.objects.filter(
                user=user
            )

    def validate_shopping_list(self, shopping_list):
        user = self.context.get('request_user')
        if user and shopping_list.user_id != user.id:
            raise serializers.ValidationError(
                'No puedes gestionar listas de otros usuarios.'
            )
        return shopping_list


class ShoppingListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    items = ShoppingListItemSerializer(many=True, read_only=True)
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    remaining_budget = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
        allow_null=True,
    )
    total_items = serializers.IntegerField(read_only=True)
    purchased_items = serializers.IntegerField(read_only=True)
    pending_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = ShoppingList
        fields = [
            'id',
            'user',
            'title',
            'target_date',
            'budget',
            'items',
            'total_items',
            'purchased_items',
            'pending_items',
            'total_cost',
            'total_spent',
            'remaining_budget',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'items',
            'total_items',
            'purchased_items',
            'pending_items',
            'total_cost',
            'total_spent',
            'remaining_budget',
            'created_at',
            'updated_at',
        ]
