from rest_framework.routers import DefaultRouter
from .views import CartViewSet, OrderViewSet, ProductViewSet, CartItemViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'carts', CartViewSet)
router.register(r'cart-items', CartItemViewSet)
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = router.urls