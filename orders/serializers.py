from rest_framework import serializers

from .models import Order

from accounts.serializers import UserSerializer


class OrderSerializer(serializers.ModelSerializer):
    agent = UserSerializer(read_only=True)  
    customer = UserSerializer(read_only=True)  

    class Meta:
        model = Order
        fields = ('id', 'description', 'order_type', 'estimate',
            'status', 'created', 'updated', 'agent', 'source_desc',
        	'source_lat', 'source_long', 'destination_lat', 'customer',
            'destination_long', 'destination_desc', 'cost_delivery',
            'cost_purchase')
        read_only_fields = ('created', 'updated', 'cost_purchase', 'cost_purchase')

class OrderStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('id', 'status')

class OrderCostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('id', 'cost_delivery', 'cost_purchase')