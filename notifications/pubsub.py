from pubnub  import Pubnub

from accounts.models import User

pub_nub = Pubnub(publish_key="pub-c-e89f7f1c-cf77-42e6-9f90-6f7f09413d4d", subscribe_key="sub-c-82e403c8-0f8a-11e6-8c3e-0619f8945a4f")

def callback(message, channel):
    print(message)

    if channel.startswith('agent'):
    	update_agent_location(message, channel)
  
  
def error(message):
    print("ERROR : " + str(message))
  
  
def connect(message):
    print("CONNECTED")
  
def reconnect(message):
    print("RECONNECTED")
  
  
def disconnect(message):
    print("DISCONNECTED")

def subscribe_global():
	pub_nub.subscribe(channels='agent', callback=callback, error=callback,
                 connect=connect, reconnect=reconnect, disconnect=disconnect)

def update_agent_location(message, channel):
	try:
		agent_phone = channel[5:]

		if not agent_phone:
			return

		agent = User.objects.get(phone=agent_phone)

		location_data = message.split(',')
		latitude = location_data[0][4:]
		longitude = location_data[1][5:]

		agent.update_location(latitude, longitude)

	except:
		pass
