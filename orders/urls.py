from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
	url(r'^$', views.OrderList.as_view(), name="order-list"),
	url(r'^/open$', views.open_orders, name="order-list-open"),
	url(r'^/closed$', views.closed_orders, name="order-list-closed"),
	url(r'^/cancelled$', views.cancelled_orders, name="order-list-cancelled"),
	url(r'^/completed$', views.completed_orders, name="order-list-completed"),
	url(r'^/pending$', views.pending_orders, name="order-list-pending"),
	url(r'^/(?P<id>[0-9]+)$', views.OrderDetail.as_view(), name='order-detail'),
	url(r'^/(?P<id>[0-9]+)/assign', views.assign_agent, name='order-assign'),
	url(r'^/(?P<id>[0-9]+)/status', views.OrderStatus.as_view(), name='order-status'),
	url(r'^/(?P<id>[0-9]+)/pick', views.pick_order, name='order-pick'),
	url(r'^/(?P<id>[0-9]+)/unpick', views.unpick_order, name='order-unpick'),
	url(r'^/(?P<id>[0-9]+)/cost', views.update_cost, name='order-cost'),
]

urlpatterns = format_suffix_patterns(urlpatterns)