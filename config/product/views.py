from rest_framework.viewsets import ModelViewSet
from .serializers import ProductSerializer
from .models import Product
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permission import IsAdminOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'price']
    search_fields = ['name', 'description']