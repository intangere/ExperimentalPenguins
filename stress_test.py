import random
import string
from json import dumps
from websocket import create_connection
import time

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def username():
    name = 'Penguin_'+get_random_string(6)
    return name, dumps({'type': 'username', 'username': name})

def join(name):
    return dumps({"type":"join",
		"data":{ "username":name,
			 "current_frame":0,
			 "shape":{"x":random.randint(0, 800),
				  "y":random.randint(0, 800),
				  "width":70,
				  "height":80
				 },
			 "direction":"south",
			 "steps":0,
			 "dx":0,
			 "dy":0,
			 "room":"main"
			}
		 })

def move(name):
	return dumps({"type":"move",
		      "username":name,
		      "x2":random.randint(0, 800),"y2":random.randint(0, 800),"sx2":390,"sy2":626,
		      "direction":"south","room":"main"})

def sendMessage(name):
	return dumps({"type":"message",
			"message": 'hello!', # '#+ get_random_string(20),
			"username":name,"room":"main"})

connections = []

MAX_CONNS = 200

for i in range(MAX_CONNS):
	ws = create_connection("ws://127.0.0.1:9000/")

	name, packet = username()
	ws.send(packet)
	#ws.recv()
	ws.send(join(name))
	#ws.recv()
	connections.append({'sock': ws, 'name': name})

#time.sleep(1)

for conn in connections:
	conn['sock'].send(move(conn['name']))
	print('sent move')

for conn in connections:
	conn['sock'].send(sendMessage(conn['name']))
	print('Sent message')
	time.sleep(.05)

time.sleep(2)

for conn in connections:
	conn['sock'].send(move(conn['name']))
	print('sent move')

time.sleep(2)

for conn in connections:
	conn['sock'].send(move(conn['name']))
	print('sent move')

time.sleep(2)

for conn in connections:
	conn['sock'].close()

print("Sent")
print("Receiving...")
#result =  ws.recv()
#print("Received '%s'" % result)



