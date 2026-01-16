from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Product, Cart, CartItem, Order, OrderItem


class OrderCreateTestCase(APITestCase):
    """Order oluşturma testleri"""
    
    def setUp(self):
        """Test öncesi setup"""
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.admin = User.objects.create_user(username='admin', password='admin123', is_staff=True)
        
        # Ürün oluştur
        self.product1 = Product.objects.create(
            name='Product 1',
            description='Test product 1',
            price=100.00,
            stock=10
        )
        self.product2 = Product.objects.create(
            name='Product 2',
            description='Test product 2',
            price=50.00,
            stock=5
        )
        
        # Sepet ve ürün ekle
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item1 = CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        self.cart_item2 = CartItem.objects.create(
            cart=self.cart,
            product=self.product2,
            quantity=1
        )
    
    def test_order_create_success(self):
        """✅ Başarılı order oluşturma"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/orders/', {})
        
        # Status kontrol
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Order oluşturuldu mu?
        self.assertTrue(Order.objects.filter(user=self.user).exists())
        
        # Toplam fiyat doğru mu? (2*100 + 1*50 = 250)
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.total_price, 250.00)
        
        # Status PENDING mi?
        self.assertEqual(order.status, Order.StatusChoices.PENDING)
    
    def test_stock_decrease_after_order(self):
        """✅ Order oluşturulduktan sonra stok düşer"""
        self.client.force_authenticate(user=self.user)
        
        # Order öncesi stok
        stock_before_1 = Product.objects.get(id=self.product1.id).stock
        stock_before_2 = Product.objects.get(id=self.product2.id).stock
        
        # Order oluştur
        response = self.client.post('/api/orders/', {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Order sonrası stok
        stock_after_1 = Product.objects.get(id=self.product1.id).stock
        stock_after_2 = Product.objects.get(id=self.product2.id).stock
        
        # Stok düştü mü?
        self.assertEqual(stock_after_1, stock_before_1 - 2)  # 10 - 2 = 8
        self.assertEqual(stock_after_2, stock_before_2 - 1)  # 5 - 1 = 4
    
    def test_order_items_created(self):
        """✅ OrderItem'lar doğru oluşturuldu"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/orders/', {})
        
        order = Order.objects.get(user=self.user)
        order_items = OrderItem.objects.filter(order=order)
        
        # OrderItem sayısı doğru mu?
        self.assertEqual(order_items.count(), 2)
        
        # İlk item kontrol
        item1 = order_items.get(product=self.product1)
        self.assertEqual(item1.quantity, 2)
        self.assertEqual(item1.price, 100.00)
        
        # İkinci item kontrol
        item2 = order_items.get(product=self.product2)
        self.assertEqual(item2.quantity, 1)
        self.assertEqual(item2.price, 50.00)
    
    def test_cart_empty_after_order(self):
        """✅ Order oluşturulduktan sonra sepet temizlenir"""
        self.client.force_authenticate(user=self.user)
        
        # Order öncesi sepette ürün var
        self.assertEqual(self.cart.items.count(), 2)
        
        # Order oluştur
        response = self.client.post('/api/orders/', {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Order sonrası sepet boş
        self.assertEqual(self.cart.items.count(), 0)
    
    def test_unauthenticated_cannot_create_order(self):
        """❌ Kimlik doğrulmamış kullanıcı order oluşturamaz"""
        response = self.client.post('/api/orders/', {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_empty_cart_cannot_create_order(self):
        """❌ Boş sepetten order oluşturulamaz"""
        self.client.force_authenticate(user=self.user)
        
        # Sepeti temizle
        self.cart.items.all().delete()
        
        response = self.client.post('/api/orders/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('empty', response.data[0].lower())


class OrderPaymentTestCase(APITestCase):
    """Order ödeme testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.product = Product.objects.create(
            name='Product',
            description='Test',
            price=100.00,
            stock=10
        )
        
        # Order oluştur
        self.order = Order.objects.create(
            user=self.user,
            total_price=100.00,
            status=Order.StatusChoices.PENDING
        )
    
    def test_payment_success(self):
        """✅ Ödeme başarılı - status COMPLETED olur"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(f'/api/orders/{self.order.order_id}/pay/', {})
        
        # Status kontrol
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Order status güncellendi mi?
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.StatusChoices.COMPLETED)
    
    def test_cannot_pay_completed_order(self):
        """❌ Zaten ödenen order ödenenemez"""
        self.client.force_authenticate(user=self.user)
        
        # Order'ı completed yap
        self.order.status = Order.StatusChoices.COMPLETED
        self.order.save()
        
        # Ödeme yapmaya çalış
        response = self.client.post(f'/api/orders/{self.order.order_id}/pay/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OrderCancelTestCase(APITestCase):
    """Order iptal testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.admin = User.objects.create_user(username='admin', password='admin123', is_staff=True)
        
        self.product = Product.objects.create(
            name='Product',
            description='Test',
            price=100.00,
            stock=10
        )
        
        # Order oluştur
        self.order = Order.objects.create(
            user=self.user,
            total_price=200.00,
            status=Order.StatusChoices.PENDING
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=100.00
        )
        
        # Stok düş
        self.product.stock = 8
        self.product.save()
    
    def test_cancel_restores_stock(self):
        """✅ Order iptal edildiğinde stok geri verilir"""
        self.client.force_authenticate(user=self.user)
        
        # İptal öncesi stok
        stock_before = Product.objects.get(id=self.product.id).stock  # 8
        
        # Order iptal et
        response = self.client.post(f'/api/orders/{self.order.order_id}/cancel/', {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Stok geri verildi mi?
        stock_after = Product.objects.get(id=self.product.id).stock
        self.assertEqual(stock_after, stock_before + 2)  # 8 + 2 = 10
    
    def test_cancel_changes_status(self):
        """✅ Order iptal edildiğinde status CANCELED olur"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(f'/api/orders/{self.order.order_id}/cancel/', {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.StatusChoices.CANCELED)
    
    def test_cannot_cancel_completed_order(self):
        """❌ Tamamlanan order iptal edilemez"""
        self.client.force_authenticate(user=self.user)
        
        # Order'ı completed yap
        self.order.status = Order.StatusChoices.COMPLETED
        self.order.save()
        
        response = self.client.post(f'/api/orders/{self.order.order_id}/cancel/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OrderPermissionTestCase(APITestCase):
    """Order izin/güvenlik testleri"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='test123')
        self.user2 = User.objects.create_user(username='user2', password='test123')
        self.admin = User.objects.create_user(username='admin', password='admin123', is_staff=True)
        
        # User1 order oluştur
        self.order1 = Order.objects.create(
            user=self.user1,
            total_price=100.00,
            status=Order.StatusChoices.PENDING
        )
        
        # User2 order oluştur
        self.order2 = Order.objects.create(
            user=self.user2,
            total_price=200.00,
            status=Order.StatusChoices.PENDING
        )
    
    def test_user_can_see_own_order(self):
        """✅ User kendi order'ını görebilir"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f'/api/orders/{self.order1.order_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_cannot_see_other_order(self):
        """❌ User başkasının order'ını göremez"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f'/api/orders/{self.order2.order_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_admin_can_see_all_orders(self):
        """✅ Admin tüm order'ları görebilir"""
        self.client.force_authenticate(user=self.admin)
        
        response = self.client.get(f'/api/orders/{self.order1.order_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(f'/api/orders/{self.order2.order_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_cannot_cancel_other_order(self):
        """❌ User başkasının order'ını iptal edemez"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.post(f'/api/orders/{self.order2.order_id}/cancel/', {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_cancel_any_order(self):
        """✅ Admin herhangi bir order'ı iptal edebilir"""
        self.client.force_authenticate(user=self.admin)
        
        response = self.client.post(f'/api/orders/{self.order1.order_id}/cancel/', {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.status, Order.StatusChoices.CANCELED)
