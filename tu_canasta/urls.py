from django.urls import path
from rest_framework.routers import DefaultRouter

urlpatterns = [
    # Add your URL patterns here
]

router = DefaultRouter()
# Register your viewsets here
# router.register(r'example', ExampleViewSet)

urlpatterns += router.urls
