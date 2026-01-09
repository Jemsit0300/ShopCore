from rest_framework import serializers
from .models import Product, Cart, CartItem

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
    # PATCH için mevcut instance'tan al
        product = self.instance.product if self.instance else None
        quantity = data.get('quantity', self.instance.quantity)

        if quantity < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")

        if product and quantity > product.stock:
            raise serializers.ValidationError(
                f"Only {product.stock} items available in stock."
            )

        return data

