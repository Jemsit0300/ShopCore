from rest_framework import serializers
from .models import Order, OrderItem, Product, Cart, CartItem
from django.db import transaction
from django.db.models import F

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'created_at']
   
class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at']
        read_only_fields = ['user']


class CartItemSerializer(serializers.ModelSerializer): 

    product = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity']


    def validate(self, data):
        product = self.instance.product if self.instance else data.get('product', None)
        
        if self.instance:
            quantity = data.get('quantity', self.instance.quantity)
        else:
            quantity = data.get('quantity')

        if quantity is None:
            raise serializers.ValidationError("Quantity is required.")

        if quantity < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")

        if product and hasattr(product, 'stock') and quantity > product.stock:
            raise serializers.ValidationError(
                f"Only {product.stock} items available in stock."
            )

        return data



class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'user', 'total_price', 'created_at', 'status']
        read_only_fields = ['order_id', 'user', 'total_price', 'created_at', 'status']

    def create(self, validated_data):
        user = self.context['request'].user

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart does not exist.")

        cart_items = cart.items.select_related('product')

        if not cart_items.exists():
            raise serializers.ValidationError("Cart is empty, cannot create order.")

        with transaction.atomic():

            product_ids = [item.product_id for item in cart_items]
            products = Product.objects.select_for_update().filter(id__in=product_ids)

            product_map = {p.id: p for p in products}
            for item in cart_items:
                product = product_map[item.product_id]
                if product.stock < item.quantity:
                    raise serializers.ValidationError(
                        f"Not enough stock for {product.name}. "
                        f"Available: {product.stock}, Requested: {item.quantity}"
                    )

            total_price = sum(
                product_map[item.product_id].price * item.quantity
                for item in cart_items
            )

            order = Order.objects.create(
                user=user,
                total_price=total_price
            )

            order_items = []

            for item in cart_items:
                product = product_map[item.product_id]

                order_items.append(
                    OrderItem(
                        order=order,
                        product=product,
                        quantity=item.quantity,
                        price=product.price
                    )
                )

                product.stock = F('stock') - item.quantity
                product.save(update_fields=['stock'])

            OrderItem.objects.bulk_create(order_items)

            cart.items.all().delete()

            return order