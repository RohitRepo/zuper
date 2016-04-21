from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
	url(r'^/getOtp$', views.getOtp, name="auth-get-otp"),
	url(r'^/login', views.login_user, name='auth-login'),
	url(r'^/logout', views.logout_user, name='auth-logout'),
	url(r'^/me$', views.UserMeDetail.as_view(), name='user-me'),
	url(r'^/me/orders$', views.my_orders, name='my-orders'),
	url(r'^/me/address', views.UserAddressList.as_view(), name='user-address'),
	url(r'^/(?P<id>[0-9]+)', views.UserDetail.as_view(), name='user-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)