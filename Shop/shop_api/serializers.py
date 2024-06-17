from rest_framework import serializers
from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price']


class OrderSerializer(serializers.ModelSerializer):
    product_ids = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True, write_only=True, source='products')
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'date', 'product_ids', 'products']

    def create(self, validated_data):
        products = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        order.products.set(products)
        return order

    def update(self, instance, validated_data):
        products = validated_data.pop('products')
        instance = super().update(instance, validated_data)
        instance.products.set(products)
        return instance

