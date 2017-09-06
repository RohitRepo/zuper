from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
	url(r'^/getOtp$', views.getOtp, name="auth-get-otp"),
	url(r'^/login', views.login_user, name='auth-login'),
	url(r'^/logout', views.logout_user, name='auth-logout'),
	url(r'^/me$', views.UserMeDetail.as_view(), name='user-me'),
	url(r'^/dump$', views.UserDumpView.as_view(), name='user-dump'),
	url(r'^/dump1$', views.UserDumpView1.as_view(), name='user-dump1'),
	url(r'^/me/gcm$', views.UpdateGCMToken.as_view(), name='update-gcm-token'),
	url(r'^/me/address', views.UserAddressList.as_view(), name='user-address'),
	url(r'^/address/(?P<id>[0-9]+)', views.UserAddressDetail.as_view(), name='address-detail'),
	url(r'^/active-agents', views.active_agents, name='active-agents'),
]

# Order Urls

urlpatterns += [
	url(r'^/me/orders$', views.my_orders, name='my-orders'),
	url(r'^/me/orders/open$', views.my_orders_open, name='my-orders-opn'),
	url(r'^/me/orders/closed$', views.my_orders_closed, name='my-orders-opn'),
	url(r'^/me/assigned$', views.assigned_orders, name='my-assigned_orders'),
]

urlpatterns = format_suffix_patterns(urlpatterns)