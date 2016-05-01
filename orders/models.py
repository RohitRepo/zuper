from django.db import models
from django.conf import settings

from zuper.models import BaseModel

class Order(BaseModel):
    TYPE_PURCHASE = 'PU'
    TYPE_DELIVERY = 'DL'

    TYPE_CHOICES = (
        (TYPE_PURCHASE, 'Purchase'),
        (TYPE_DELIVERY, 'Delivery'),
    )

    STATUS_PENDING = 'PN'
    STATUS_ACCEPTED = 'AC'
    STATUS_PICKED = 'PK'
    STATUS_PURCHASED = 'PR'
    STATUS_DELIVERY = 'DV'
    STATUS_COMPLETED = 'CM'
    STATUS_CANCELLED = 'CN'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_PICKED, 'Picked'),
        (STATUS_PURCHASED, 'Purchased'),
        (STATUS_DELIVERY, 'Delivery'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="orders")
    description = models.TextField()
    order_type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    estimate = models.IntegerField(blank=True, null=True)

    destination_desc = models.TextField()
    destination_lat = models.CharField(max_length=10)
    destination_long = models.CharField(max_length=10)
    source_desc = models.TextField(blank=True)
    source_lat = models.CharField(max_length=10, blank=True)
    source_long = models.CharField(max_length=10, blank=True)

    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=STATUS_PENDING)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="updates", blank=True, null=True)

    agent = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="picks", blank=True, null=True)
    cost_delivery = models.IntegerField(blank=True, null=True)
    cost_purchase = models.IntegerField(blank=True, null=True)

    def is_owner(self, user):
        return user.id == self.customer.id

    def is_assigned(self, user):

        if not self.agent:
            return False

        return self.agent.id == user.id
