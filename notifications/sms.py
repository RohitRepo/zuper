from random import randint
from twilio.rest import TwilioRestClient

account_sid = "AC12e8c7a5d77e38af9d125543bae9fd9d"
auth_token = "efd7428f3fe2e97479326f691ccaab10"
client = TwilioRestClient(account_sid, auth_token)

def send_otp(phone, otp):
	phone = '+91' + phone
	message = 'Your OTP for registration of zuperfast app is: ' + otp

	message = client.messages.create(to=phone,
		from_="+12013405198",
		body=message
	)

def generate_otp():
	return str(randint(1000, 9999))