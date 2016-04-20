import os

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings

from zuper.models import BaseModel

from .usermanager import UserManager, UserOtpManager

class User(AbstractBaseUser, PermissionsMixin):

    name = models.CharField(max_length=80)
    email = models.EmailField(max_length=255, blank=True)
    phone = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True,)
    date_joined = models.DateTimeField(auto_now_add=True,)

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
        return self.get_full_name()

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        "Returns the short name for the user."
        return self.name

    def activate(self):
    	if not self.is_active:
    		self.is_active = True
    		self.save()


class UserOtp(BaseModel):
	otp = models.CharField(max_length=6)
	user = models.OneToOneField(User)

	objects = UserOtpManager()

class UserAddress(BaseModel):
	user = models.OneToOneField(User)
	address = models.CharField(max_length=200)
	latitude = models.CharField(max_length=15)
	longitude = models.CharField(max_length=15)
