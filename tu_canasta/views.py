from django.db import IntegrityError
from django.urls import reverse as django_reverse
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import Product, ShoppingList, ShoppingListItem, User
from .serializers import (
    ProductSerializer,
    ShoppingListItemSerializer,
    ShoppingListSerializer,
    UserSerializer,
)


def _get_request_user(request) -> User:
    user_identifier = (
        request.headers.get('X-USER-ID') or request.query_params.get('user_id')
    )
    if not user_identifier:
        raise AuthenticationFailed(
            'Proporciona el encabezado X-USER-ID o el parámetro user_id.'
        )
    try:
        return User.objects.get(pk=user_identifier)
    except (ValueError, User.DoesNotExist) as exc:
        raise AuthenticationFailed('Usuario no encontrado.') from exc


@api_view(['GET'])
def api_root(request, format=None):
    """
    Root entry point rendered with DRF's browsable API.
    Provides quick links to the main sections of the backend.
    """
    return Response(
        {
            "admin": request.build_absolute_uri(django_reverse('admin:index')),
            "users": reverse('user-list', request=request, format=format),
            "products": reverse('product-list', request=request, format=format),
            "shopping_lists": reverse('shopping-list-list', request=request, format=format),
            "shopping_list_items": reverse(
                'shopping-list-item-list', request=request, format=format
            ),
        }
    )


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD for application users.
    Passwords are hashed before saving through the serializer.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    Basic CRUD for products available in the inventory.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ShoppingListViewSet(viewsets.ModelViewSet):
    """
    Allows each user to maintain an independent shopping list.
    Access is restricted via the X-USER-ID header or user_id query parameter.
    """
    serializer_class = ShoppingListSerializer

    def get_queryset(self):
        user = self._get_user()
        return ShoppingList.objects.filter(user=user).prefetch_related('items__product')

    def _get_user(self) -> User:
        if not hasattr(self.request, '_cached_user_object'):
            self.request._cached_user_object = _get_request_user(self.request)
        return self.request._cached_user_object

    def perform_create(self, serializer):
        user = self._get_user()
        try:
            serializer.save(user=user)
        except IntegrityError as exc:
            raise ValidationError(
                'El usuario ya tiene una lista de compras registrada.'
            ) from exc


class ShoppingListItemViewSet(viewsets.ModelViewSet):
    """
    CRUD for the products assigned to a user's shopping list.
    Each user only manipulates their own list entries.
    """
    serializer_class = ShoppingListItemSerializer

    def get_queryset(self):
        user = self._get_user()
        return (
            ShoppingListItem.objects.filter(shopping_list__user=user)
            .select_related('product', 'shopping_list__user')
        )

    def _get_user(self) -> User:
        if not hasattr(self.request, '_cached_user_object'):
            self.request._cached_user_object = _get_request_user(self.request)
        return self.request._cached_user_object

    def perform_create(self, serializer):
        user = self._get_user()
        shopping_list, _ = ShoppingList.objects.get_or_create(user=user)
        serializer.save(shopping_list=shopping_list)

    def perform_update(self, serializer):
        user = self._get_user()
        if serializer.instance.shopping_list.user_id != user.id:
            raise AuthenticationFailed('No puedes modificar listas de otros usuarios.')
        serializer.save()

    def perform_destroy(self, instance):
        user = self._get_user()
        if instance.shopping_list.user_id != user.id:
            raise AuthenticationFailed('No puedes eliminar listas de otros usuarios.')
        instance.delete()
