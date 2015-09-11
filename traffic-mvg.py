import paho.mqtt.client as mqtt
import MVGLive
import time
import config
import requests

def on_connect(mosq, obj, rc):
	print("Connect with RC " + str(rc))

def on_disconnect(client, userdata, rc):
	print("Disconnected (RC " + str(rc) + ")")

def on_log(client, userdata, level, buf):
	print(buf)

mqttc = mqtt.Client("")
mqttc.username_pw_set(config.username, config.password)
# mqttc.connect(config.host, config.port, 60)
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_log = on_log

foo = MVGLive.MVGLive()

state = "000"

state_1 = True
state_2 = True
state_3 = True


# Sets light to state (Only sends MQTT message if state changed)
def set_single_light(light, state):
	global state_1
	global state_2
	global state_3

	if light == 1 and state_1 != state:
		mqttc.publish(config.topic_red, int(state), 1, False)
		state_1 = state
	elif light == 2 and state_2 != state:
		mqttc.publish(config.topic_yellow, int(state), 1, False)
		state_2 = state
	elif light == 3 and state_3 != state:
		mqttc.publish(config.topic_green, int(state), 1, False)
		state_3 = state

# Sets the traffic light to (only) off, red, yellow, green
def set_traffic_light(light):
	global state
	if light == 0 and state != "000":
		connect_once()
		mqttc.publish(config.topic_ryg, "000", 1, False)
		state = "000"
		mqttc.disconnect()
	elif light == 1 and state != "100":
		connect_once()
		mqttc.publish(config.topic_ryg, "100", 1, False)
		state = "100"
		mqttc.disconnect()
	elif light == 2 and state != "010":
		connect_once()
		mqttc.publish(config.topic_ryg, "010", 1, False)
		state = "010"
		mqttc.disconnect()
	elif light == 3 and state != "001":
		connect_once()
		mqttc.publish(config.topic_ryg, "001", 1, False)
		state = "001"
		mqttc.disconnect()
	elif light == 4 and state != "110":
		connect_once()
		mqttc.publish(config.topic_ryg, "110", 1, False)
		state = "110"
		mqttc.disconnect()

def connect_once():
	try:
		mqttc.reconnect()
	except Exception as e:
		print("Failed to connect to mqtt. Retrying...")
		time.sleep(5)
		return False

## Values for U-Bahn
station_u = "Obersendling"
linename_u = "U3"
destination_u = "Moosach"
walking_time_u = 5

## Values for S-Bahn

station_s = "Siemenswerke"
linename_s = "S7"
## TODO: Finish

def refresh():
	# get space status from web api
	try:
		r = requests.get(config.url)
	except Exception as e:
		print("Couldn't get space status. Retrying...")
		time.sleep(5)
		return False

	j =  r.json()
	if j[u'door'] == "open":
		## Always push U-Bahn for now.
		push(station_u, linename_u, destination_u, walking_time_u)
	else:
		try:
			mqttc.reconnect()
		except Exception as e:
			return False
		set_traffic_light(0)

		mqttc.disconnect()



def push(station, linename, destination, walking_time): # Pushes the Lines to the Display
	lifedata = None
	try:
		lifedata = foo.getlivedata(station)
	except Exception as e:
		print("Failed to get station data")
		time.sleep(5)
		return False

	reduced_lifedata = []

	for entry in lifedata:
		if entry["linename"] == linename and entry["destination"] == destination:
			reduced_lifedata.append(entry)

	if not reduced_lifedata:
		print "No more U-Bahns?"
		set_traffic_light(0)
		return
	dept = reduced_lifedata[0]


	print dept["time"]

	if dept["time"] == 8:
		print "redyellow"
		set_traffic_light(4)

	elif dept["time"] == 7 or dept["time"] == 6:
		print "green"
		set_traffic_light(3)

	elif dept["time"] == 5:
		print "yellow"
		set_traffic_light(2)

	else:
		print "red"
		set_traffic_light(1)

	mqttc.disconnect()

# Loop

def init():
	try:
		mqttc.connect(config.host, config.port, 60)
	except Exception as e:
		return False
	set_single_light(1, False)
	set_single_light(2, False)
	set_single_light(3, False)
	mqttc.disconnect()
	return True

try:
	while not init():
		print("Couldn't connect... retrying")
		time.sleep(5)
	print("Entered loop")
	while True:
		refresh()
		time.sleep(10)
except KeyboardInterrupt:
	print 'interrupted!'
	mqttc.disconnect()
