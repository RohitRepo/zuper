from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
	url(r'^$', views.OrderList.as_view(), name="order-list"),
	url(r'^/(?P<id>[0-9]+)/status', views.OrderStatus.as_view(), name='order-status'),
	url(r'^/(?P<id>[0-9]+)/pick', views.pick_order, name='order-pick'),
	url(r'^/(?P<id>[0-9]+)/cost', views.pick_order, name='order-cost'),
]

urlpatterns = format_suffix_patterns(urlpatterns)