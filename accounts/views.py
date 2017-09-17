import json, collections, ast
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .models import User, UserOtp, UserAddress, UserDump, UserDump1, UserDump2
from .serializers import UserSerializer, UserAddressSerializer, UserDumpSerializer
from .permissions import HasAddress

from orders.models import Order
from orders.serializers import OrderSerializer
from orders.permissions import IsStaff
from notifications.sms import generate_otp
from notifications.tasks import send_otp_task
from notifications.sms import send_otp

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
    # send_otp_task.delay(phone, otp)
    user = User.objects.get_or_create_dummy(phone, user_type)

    if not (user.user_type == user_type):
        return Response({"error": "Already registered in a different role"}, status=status.HTTP_400_BAD_REQUEST)

    UserOtp.objects.create_or_update(user = user, otp=otp)
    return Response() 

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def login_user(request, format=None):
    otp = request.data.get('otp')
    phone = request.data.get('phone')
    password = request.data.get('password')

    if otp:
        return login_otp(otp, phone)
    elif password:
        print 'GOT PASSWORD'
        return login_password(password, phone, request)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # TODO Validate the data

def login_otp(otp, phone):
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

def login_password(password, phone, request):
    try:
        user = User.objects.get(phone=phone)
        user = authenticate(username=phone, password=password)

        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if user.is_active:
            login(request, user)
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def logout_user(request, format=None):

    try:
        Token.objects.get(user=request.user).delete()
    except:
        pass

    try:
        logout(request)
    except:
        pass

    
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

class UserDumpView(APIView):

    def get(self, request, format=None):
        start = request.GET.get('start', 0)
        limit = request.GET.get('limit', 10)

        try:
            start = int(start)
            limit = int(limit)
        except Exception as e:
            start = 0
            limit = 10

        data = UserDump.objects.filter(id__gte=start, id__lte=start+limit)
        serializer = UserDumpSerializer(data, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        if not data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = UserDump.objects.create(data=data)
        return Response(UserDumpSerializer(data).data)

class UserDumpView1(APIView):

    def get(self, request, format=None):
        start = request.GET.get('start', 0)
        limit = request.GET.get('limit', 10)

        try:
            start = int(start)
            limit = int(limit)
        except Exception as e:
            start = 0
            limit = 10

        data = UserDump1.objects.filter(id__gte=start, id__lte=start+limit)
        serializer = UserDumpSerializer(data, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        if not data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = UserDump1.objects.create(data=data)
        return Response(UserDumpSerializer(data).data)

class UserDumpView2(APIView):

    def get(self, request, format=None):
        start = request.GET.get('start', 0)
        limit = request.GET.get('limit', 10)

        try:
            start = int(start)
            limit = int(limit)
        except Exception as e:
            start = 0
            limit = 10

        data = UserDump2.objects.filter(id__gte=start, id__lte=start+limit)
        serializer = UserDumpSerializer(data, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        if not data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = UserDump2.objects.create(data=data)
        return Response(UserDumpSerializer(data).data)

class UserDumpJsonP2(APIView):

    def get(self, request, format=None):
        start = request.GET.get('start', 0)
        limit = request.GET.get('limit', 10)
        name = request.GET.get('name', '')

        try:
            start = int(start)
            limit = int(limit)
        except Exception as e:
            start = 0
            limit = 10

        data = UserDump2.objects.filter(id__gte=start, id__lte=start+limit)
        serializer = UserDumpSerializer(data, many=True)
        data = serializer.data

        for d in data:
            if 'data' in d:
                item_data = ast.literal_eval(d['data'])
                d['data'] = item_data

        data = [d for d in data if name.lower() in d['data'].get('user', {}).get('name', '').lower()]
                
        response = 'eqfeed_callback(' + json.dumps((data)) + ')';

        return HttpResponse(response)


# Relations from other apps

def user_maps(request):
    start = request.GET.get('start', 0)
    limit = request.GET.get('limit', 10)
    name = request.GET.get('name', '')
    
    BASE_URL = '/users/dump21'
    data_url = BASE_URL + '?start={0}&limit={1}&name={2}'.format(start, limit, name)
    context = RequestContext(request, {'data_url': data_url})
    return render_to_response('maps.html', context)

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
    orders = request.user.orders.filter(Q(status=Order.STATUS_CANCELLED) | Q(status=Order.STATUS_COMPLETED))
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def assigned_orders(request, format=None):
    query = request.query_params.get('status')
    if query:
        orders = request.user.picks.filter(status=query)
    else:
        orders = request.user.picks.exclude(status=Order.STATUS_CANCELLED).exclude(status=Order.STATUS_COMPLETED)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

class UpdateGCMToken(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def put(self, request, format=None):
        user = request.user
        gcm_token = request.data.get('gcm_token')

        if gcm_token:
            user.gcm_token = gcm_token
            user.save()
            return Response()
        else:
            return Response(data={'error', 'gcm_token is required'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        request.user.gcm_token = ''
        request.user.save()
        return Response()


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, IsStaff))
def active_agents(request, format=None):
    users = User.objects.filter(user_type=User.TYPE_AGENT, is_active=True, is_online=True)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)