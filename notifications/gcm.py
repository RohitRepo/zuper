import requests, json

from orders.serializers import OrderSerializer

url = 'https://gcm-http.googleapis.com/gcm/send'
AUTHKEY = 'AIzaSyD2NUwHvqbAlE-7IAqoEBu_YhV0HEjVJ_w'
headers = {'Content-Type': 'application/json', 'Authorization': 'key='+AUTHKEY}


def send_gcm(data):
	r = requests.post(url, headers=headers, data=data)

def order_status_gcm(order, user):
	if not order or not user or user.id == order.customer.id:
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
	result = {'data': {'order': data},
		'to': user_id
	}

	return json.dumps(result)

