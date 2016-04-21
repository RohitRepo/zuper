from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('id', 'description', 'order_type', 'estimate', 'status',
        	'source_lat', 'source_long', 'destination_lat', 'destination_long', 'cost_delivery', 'cost_purchase')
        # read_only_fields = ('id', 'phone')
        # write_only_fields = ('user_type', )

class OrderStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('id', 'status')

class OrderCostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('id', 'cost_delivery', 'cost_purchase')