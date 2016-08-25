import time

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_503_SERVICE_UNAVAILABLE
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .models import Order
from .serializers import OrderSerializer, OrderStatusSerializer, OrderCostSerializer
from .permissions import IsCustomer, IsAgent, IsCreator, IsCreatorOrAgent, IsStaff
from .permissions import CanUpdateStatus, IsStaffOrCustomerWriteOnly, IsCreatorOrStaffOrAssignedTo, IsAssignedTo

from accounts.models import User
from notifications.tasks import order_status_gcm_task
from notifications.gcm import request_agent
from notifications.email import send_email

def paginate_orders(request, orders):
    paginator = PageNumberPagination()
    result_page = paginator.paginate_queryset(orders, request)
    serializer = OrderSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

class OrderList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsStaffOrCustomerWriteOnly)

    def post(self, request, format=None):
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(customer=request.user, updated_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        query = request.query_params.get('status')
        if query:
            orders = Order.objects.filter(status=query).order_by('-id')
        else:
            orders = Order.objects.all().order_by('-id')

        return paginate_orders(request, orders)


class OrderStatus(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def clean_agent_status(self, status, order):
        if status in [Order.STATUS_ACCEPTED, Order.STATUS_PICKED, Order.STATUS_PURCHASED, Order.STATUS_DELIVERY, Order.STATUS_COMPLETED]:
            return status
        elif status == Order.STATUS_CANCELLED:
            return Order.STATUS_PENDING

        return None

    def clean_customer_status(self, status, order):
        if status == Order.STATUS_CANCELLED:
            if order.status in [Order.STATUS_PENDING, Order.STATUS_ACCEPTED]:
                return status

        return None

    def clean_staff_status(self, status, order):
        if status == Order.STATUS_CANCELLED:
            return status

        return None

    def put(self, request, id, format=None):
        order = get_object_or_404(Order, id=id)
        self.check_object_permissions(request, order)
        serializer = OrderStatusSerializer(order, request.data)

        if serializer.is_valid():

            if request.user.id == order.customer.id:
                order_status = self.clean_customer_status(request.data.get('status'), order)
            elif order.agent and order.agent.id == request.user.id:
                order_status = self.clean_agent_status(request.data.get('status'), order)
            elif request.user.is_staff:
                order_status = self.clean_staff_status(request.data.get('status'), order)

            if not order_status:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            order = serializer.save(updated_by=request.user, status=order_status)

            order_status_gcm_task.delay(order, order.customer)
            if order.status == Order.STATUS_CANCELLED and order.agent:
                order_status_gcm_task.delay(order, order.agent)

            serializer = OrderSerializer(order)
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCreatorOrStaffOrAssignedTo)

    def get(self, request, id, format=None):
        order = get_object_or_404(Order, id=id)
        serializer = OrderSerializer(order)
        return Response(data=serializer.data)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, IsAgent))
def pick_order(request, id, format=None):
    order = get_object_or_404(Order, id=id)
    order.agent = request.user
    order.status = Order.STATUS_ACCEPTED
    order.updated_by = request.user
    order.save()

    serializer = OrderSerializer(order)
    return Response(data=serializer.data)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, IsAssignedTo))
def unpick_order(request, id, format=None):
    order = get_object_or_404(Order, id=id)
    order.agent = None
    order.status = Order.STATUS_PENDING
    order.updated_by = request.user
    order.save()

    serializer = OrderSerializer(order)
    return Response(data=serializer.data)
    

@api_view(['PUT'])
@permission_classes((permissions.IsAuthenticated, IsAgent))
def update_cost(request, id, format=None):
    order = get_object_or_404(Order, id=id)
    serializer = OrderCostSerializer(order, request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(data=serializer.data)
    else:
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, IsStaff))
def pending_orders(request, format=None):
    orders = Order.objects.filter(status=Order.STATUS_PENDING).order_by('-id')
    return paginate_orders(request, orders)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, IsStaff))
def open_orders(request, format=None):
    orders = Order.objects.exclude(status=Order.STATUS_CANCELLED).exclude(status=Order.STATUS_PENDING).exclude(status=Order.STATUS_COMPLETED).order_by('-id')
    return paginate_orders(request, orders)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, IsStaff))
def closed_orders(request, format=None):
    orders = Order.objects.filter(Q(status=Order.STATUS_CANCELLED) | Q(status=Order.STATUS_COMPLETED)).order_by('-id')
    return paginate_orders(request, orders)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, IsStaff))
def cancelled_orders(request, format=None):
    orders = Order.objects.filter(status=Order.STATUS_CANCELLED).order_by('-id')
    return paginate_orders(request, orders)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, IsStaff))
def completed_orders(request, format=None):
    orders = Order.objects.filter(status=Order.STATUS_COMPLETED).order_by('-id')
    return paginate_orders(request, orders)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, IsStaff))
def assign_agent(request, id, format=None):
    order = get_object_or_404(Order, id=id)

    # TODO handle existing agent better
    order.agent = None
    order.status = Order.STATUS_PENDING
    order.updated_by = request.user
    order.save()

    user_id = request.data.get('user_id')
    if not user_id:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, id=user_id)
    request_agent(user, order)

    # count = 0
    # while(count < 60):
    #     time.sleep(5)
    #     order = get_object_or_404(Order, id=id)
    #     if order.agent:
    #         serializer = OrderSerializer(order)
    #         return Response(data=serializer.data)

    #     count += 5

    return Response()

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, IsCreator))
def mail_order(request, id, format=None):
    order = get_object_or_404(Order, id=id)
    email = request.user.email

    if email is None:
        body = { 'message' : 'E-Mail id not saved'}
        return Response(status=HTTP_404_NOT_FOUND, data=body)

    subject = "Order Bill - " + str(order.id)
    message = "Here is your order bill"
    from_email = "orders@zuperfast.com"

    email_status = send_email(email, from_email, subject, message)
    if not email_status:
        body = { 'message', 'Email service failed'}
        return Response(status=HTTP_503_SERVICE_UNAVAILABLE, data=body)

    body = { 'message' : 'Email sent to {0}'.format(email),}
    return Response(data=body)
