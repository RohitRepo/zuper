import requests

from orders.serializers import OrderSerializer

url = 'https://gcm-http.googleapis.com/gcm/send'
AUTHKEY = 'sdfsdfgsdfgsdf'
headers = {'Content-Type': 'application/json', 'Authorization': 'key='+AUTHKEY}


def send_gcm(data):
	r = requests.post(url, headers=headers, data=data)

def order_status_gcm(data, user):
	if not data or not user or user.id == order.customer.id:
		return

	user_id = user.gcm_token
	if user_id:
		data = get_order_status_data(order, user_id)
		send_gcm(data)

def get_order_status_data(order, user_id):
	if not order:
		return

	serializer = OrderSerializer(order)
	return wrap_with_id(serializer.data, user_id)

def wrap_with_id(data, user_id):
	return {'data': data,
		'to': user_id
	}

