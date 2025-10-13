from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import User
from .serializers import UserSerializer


@api_view(['GET'])
def api_root(request, format=None):
    """
    Root entry point rendered with DRF's browsable API.
    Provides quick links to the main sections of the backend.
    """
    return Response(
        {
            "admin": request.build_absolute_uri(reverse('admin:index')),
            "users": request.build_absolute_uri(reverse('user-list', request=request, format=format)),
            "api_docs": request.build_absolute_uri('/api/'),
        }
    )


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD for application users.
    Passwords are hashed before saving through the serializer.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
