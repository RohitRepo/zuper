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
	pub_nub.subscribe(channels='agent', callback=callback, error=callback, connect=connect, reconnect=reconnect, disconnect=disconnect)

def update_agent_location(message, channel):
	agent_id = message.get('agent')

	if not agent_id:
		return

	agent = User.objects.get(id=agent_id)

	latitude = message.get('latitude')
	longitude = message.get('longitude')

	agent.update_location(latitude, longitude)

