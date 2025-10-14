from rest_framework.routers import DefaultRouter

from .views import (
    ProductViewSet,
    ShoppingListItemViewSet,
    ShoppingListViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'shopping-lists', ShoppingListViewSet, basename='shopping-list')
router.register(
    r'shopping-list-items', ShoppingListItemViewSet, basename='shopping-list-item'
)

urlpatterns = router.urls
