from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .models import User, UserOtp, UserAddress
from .serializers import UserSerializer, UserAddressSerializer


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def getOtp(request, format=None):
    phone = request.data.get('phone')

    if not phone:
        # TODO better phone number validation
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # OTP generation logic
    otp = '1234'
    user = User.objects.get_or_create_dummy(phone)
    UserOtp.objects.create_or_update(user = user, otp=otp)
    return Response(data={'otp': '1234'}) 

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def login_user(request, format=None):
    otp = request.data.get('otp')
    phone = request.data.get('phone')

    # TODO Validate the data

    if (UserOtp.objects.checkOtp(otp, phone)):
        user = User.objects.get(phone=phone)
        user.activate()

        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        data = UserSerializer(user).data
        data['token'] = token.key
        return Response(data=data)
    else:
        return Response(data={"error": "Invalid OTP"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def logout_user(request, format=None):
    Token.objects.get(user=request.user).delete()
    return Response()

class UserMe(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, format=None):
        serializer = UserSerializer(request.user, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return Response(data=serializer.data)

class UserAddressList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        try:
            address = request.user.useraddress
            serializer = UserAddressSerializer(address, data=request.data)
        except ObjectDoesNotExist:
            serializer = UserAddressSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        try:
            address = request.user.useraddress
            serializer = UserAddressSerializer(address)
            return Response(data=serializer.data)
        except ObjectDoesNotExist:
            return Response(data={})
