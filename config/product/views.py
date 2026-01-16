from rest_framework.viewsets import ModelViewSet
from .serializers import CartSerializer, ProductSerializer, CartItemSerializer
from .models import CartItem
from .models import Cart, Product
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db import models
from .permission import IsAdminOrReadOnly, IsAdminOrOwner
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from .models import Order
from .serializers import OrderCreateSerializer
from rest_framework.decorators import action
from rest_framework import status
from django.db import transaction
from .throttles import UserThrottle, AnonRateThrottle
from product.throttles import OrderUserThrottle, OrderAnonThrottle, PaymentUserThrottle
from django.core.cache import cache

PRODUCT_LIST_CACHE_KEY = "product_list"
PRODUCT_LIST_CACHE_TTL = 60 * 5  # 5 minutes



class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'price']
    search_fields = ['name', 'description']
    throttle_classes = [UserThrottle, AnonRateThrottle]

    def list(self, request, *args, **kwargs):
        cached_data = cache.get(PRODUCT_LIST_CACHE_KEY)

        if cached_data:
            return Response(cached_data)
        
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        cache.set(
            PRODUCT_LIST_CACHE_KEY,
            serializer.data,
            PRODUCT_LIST_CACHE_TTL
        )

        return Response(serializer.data)
    
    def perform_create(self, serializer):
        serializer.save()
        cache.delete(PRODUCT_LIST_CACHE_KEY)

    def perform_update(self, serializer):
        serializer.save()
        cache.delete(PRODUCT_LIST_CACHE_KEY)

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete(PRODUCT_LIST_CACHE_KEY)

class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination for carts

    def get_queryset(self):
        return (
            Cart.objects
            .filter(user=self.request.user)
            .select_related('user')
            .prefetch_related('items__product')
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            CartItem.objects
            .filter(cart__user=self.request.user)
            .select_related('cart', 'product')
        )
    
    def perform_create(self, serializer):
        cart = Cart.objects.get(user=self.request.user)
        serializer.save(cart=cart)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]
    throttle_classes = [OrderUserThrottle, OrderAnonThrottle]

    def get_queryset(self):
        # Admin tüm siparişleri görebilir, user sadece kendi siparişlerini
        if self.request.user.is_staff:
            return (
                Order.objects.all()
                .select_related('user')
                .prefetch_related('order_items__product')
            )
        return (
            Order.objects
            .filter(user=self.request.user)
            .select_related('user')
            .prefetch_related('order_items__product')
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=True, methods=['post'], throttle_classes=[PaymentUserThrottle])
    def pay(self, request, pk=None):
        order = self.get_object()
        
        if order.status != Order.StatusChoices.PENDING:
            return Response({"detail": "Order cannot be paid."}, 
                            status=status.HTTP_400_BAD_REQUEST
                            )
        
        with transaction.atomic():
            order.status = Order.StatusChoices.COMPLETED
            order.save()

        return Response(
            {"detail": "Payment successful."}, 
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], throttle_classes=[OrderUserThrottle])
    def cancel(self, request, pk=None):
        order = self.get_object()
        
        if order.status != Order.StatusChoices.PENDING:
            return Response(
                {"detail": "Only pending orders can be canceled."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Stoğu geri ver
            for order_item in order.order_items.select_related('product'):
                product = order_item.product
                product.stock = models.F('stock') + order_item.quantity
                product.save(update_fields=['stock'])
            
            # Siparişi iptal et
            order.status = Order.StatusChoices.CANCELED
            order.save()
        
        return Response(
            {"detail": "Order canceled successfully. Stock restored."}, 
            status=status.HTTP_200_OK
        )