from random import randint
from twilio.rest import TwilioRestClient
 
account_sid = "AC1a2125e3158a5cc169ffab955ca3e0b7"
auth_token = "5cf455090ceab9211f33d66b0706f4f1"
client = TwilioRestClient(account_sid, auth_token)

def send_otp(phone, otp):
	phone = '+91' + phone
	message = 'Your OTP for registration is: ' + otp

	message = client.messages.create(to=phone,
		from_="+17757493062",
		body=message
	)

def generate_otp():
	return str(randint(1000, 9999))