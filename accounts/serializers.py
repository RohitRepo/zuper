from rest_framework import serializers
from .models import User, UserAddress


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'phone','name', 'email', 'user_type', 'latitude', 'longitude')
        read_only_fields = ('id', 'phone', 'latitude', 'longitude')
        write_only_fields = ('user_type', )


class UserAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAddress
        fields = ('id', 'address','latitude', 'longitude', 'tag')
