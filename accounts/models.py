import os

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings

from zuper.models import BaseModel

from .usermanager import UserManager, UserOtpManager

class User(AbstractBaseUser, PermissionsMixin):
    TYPE_CUSTOMER = 'CU'
    TYPE_AGENT = 'AG'

    TYPE_CHOICES = (
        (TYPE_CUSTOMER, 'Customer'),
        (TYPE_AGENT, 'Agent'),
    )

    name = models.CharField(max_length=80)
    email = models.EmailField(max_length=255, blank=True)
    phone = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True,)
    date_joined = models.DateTimeField(auto_now_add=True,)
    user_type = models.CharField(max_length=2, choices=TYPE_CHOICES, default=TYPE_CUSTOMER)
    gcm_token = models.CharField(max_length=500, blank=True)
    latitude = models.CharField(max_length=15, blank=True)
    longitude = models.CharField(max_length=15, blank=True)
    is_staff = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def save(self, *args, **kwargs):
        new = False
        if self.pk is None:
            new = True

        super(User, self).save(*args, **kwargs)

        # if new and self.is_active:
        #     send_welcome_mail.delay(self.id)

    def __unicode__(self):
        return self.get_full_name() + ": " + str(self.phone)

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        "Returns the short name for the user."
        return self.name

    def activate(self):
        if not self.is_active:
            self.is_active = True
            self.save()

    def is_customer(self):
        return self.user_type == self.TYPE_CUSTOMER

    def is_agent(self):
        return self.user_type == self.TYPE_AGENT

    def update_location(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.save()

    def update_online(self, status):
        self.is_online = status
        self.save()


class UserOtp(BaseModel):
    otp = models.CharField(max_length=6)
    user = models.OneToOneField(User)

    objects = UserOtpManager()

class UserAddress(BaseModel):
    user = models.ForeignKey(User, related_name="addresses")
    tag = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=200)
    latitude = models.CharField(max_length=30)
    longitude = models.CharField(max_length=30)

class UserDump(BaseModel):
    data = models.TextField(blank=True, null=True)

class UserDump1(BaseModel):
    data = models.TextField(blank=True, null=True)
