from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .models import Order
from .serializers import OrderSerializer, OrderStatusSerializer, OrderCostSerializer
from .permissions import IsCustomer, IsAgent, IsCreator, IsCreatorOrAgent
from .permissions import CanUpdateStatus, IsCustomerOrReadOnly, IsCreatorOrAssignedTo, IsAssignedTo

class OrderList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCustomerOrReadOnly)

    def post(self, request, format=None):
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(customer=request.user, updated_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        orders = Order.objects.filter(status=Order.STATUS_PENDING)

        serializer = OrderSerializer(orders, many=True)
        return Response(data=serializer.data)


class OrderStatus(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCreatorOrAgent, CanUpdateStatus)

    def put(self, request, id, format=None):
        order = get_object_or_404(Order, id=id)
        self.check_object_permissions(request, order)
        serializer = OrderStatusSerializer(order, request.data)

        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            serializer = OrderSerializer(order)
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, IsCreatorOrAssignedTo)

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
