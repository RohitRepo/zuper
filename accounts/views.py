from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .models import User, UserOtp, UserAddress
from .serializers import UserSerializer, UserAddressSerializer
from .sms import send_otp, generate_otp
from .permissions import HasAddress

from orders.serializers import OrderSerializer


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def getOtp(request, format=None):
    phone = request.data.get('phone')
    user_type = request.data.get('type')

    if not phone:
        # TODO better phone number validation
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if not (user_type == User.TYPE_AGENT):
        user_type = User.TYPE_CUSTOMER


    # OTP generation logic
    # otp = generate_otp()
    otp = '1234'
    # send_otp(phone, otp)
    user = User.objects.get_or_create_dummy(phone, user_type)
    UserOtp.objects.create_or_update(user = user, otp=otp)
    return Response() 

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

class UserMeDetail(APIView):
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

class UserDetail(APIView):
    # TODO Add permission for only super user to see this
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id, format=None):
        user = get_object_or_404(user, id=id)
        serializer = UserSerializer(user)
        return Response(data=serializer.data)

class UserAddressList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        serializer = UserAddressSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        try:
            addresses = request.user.addresses.all()
            serializer = UserAddressSerializer(addresses, many=True)
            return Response(data=serializer.data)
        except ObjectDoesNotExist:
            return Response(data={})

class UserAddressDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, HasAddress)

    def put(self, request, id, format=None):
        try:
            address = request.user.addresses.get(id=id)
            serializer = UserAddressSerializer(address, data=request.data)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id, format=None):
        try:
            address = request.user.addresses.get(id=id)
            serializer = UserAddressSerializer(address, data=request.data)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.data)

    def delete(self, request, id, format=None):
        try:
            address = request.user.addresses.get(id=id)
            address.delete()            
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response()


# Relations from other apps

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def my_orders(request, format=None):
    query = request.query_params.get('status')
    if query:
        orders = request.user.orders.filter(status=query)
    else:
        orders = request.user.orders
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def my_orders_open(request, format=None):
    orders = request.user.orders.exclude(status=Order.STATUS_CANCELLED).exclude(status=Order.STATUS_COMPLETED)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def my_orders_closed(request, format=None):
    orders = request.user.orders.filter(status=Order.STATUS_CANCELLED).filter(status=Order.STATUS_COMPLETED)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def assigned_orders(request, format=None):
    query = request.query_params.get('status')
    if query:
        orders = request.user.picks.filter(status=query)
    else:
        orders = request.user.picks
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)