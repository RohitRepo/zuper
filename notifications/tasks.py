from __future__ import absolute_import

from celery import shared_task

from .sms import send_otp
from .gcm import order_status_gcm

@shared_task
def send_otp_task(phone, otp):
    send_otp(phone, otp)

@shared_task
def order_status_gcm_task(data, user):
	order_status_gcm(data, user)