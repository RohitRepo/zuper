from rest_framework import serializers
from .models import User, UserAddress


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'phone','name', 'email')
        read_only_fields = ('id', 'phone')


class UserAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAddress
        fields = ('id', 'address','latitude', 'longitude')
