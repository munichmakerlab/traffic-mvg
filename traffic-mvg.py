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
	if light == 0:
		set_single_light(1, False)
		set_single_light(2, False)
		set_single_light(3, False)
	elif light == 1:
		set_single_light(1, True)
		set_single_light(2, False)
		set_single_light(3, False)
	elif light == 2:
		set_single_light(1, False)
		set_single_light(2, True)
		set_single_light(3, False)
	elif light == 3:
		set_single_light(1, False)
		set_single_light(2, False)
		set_single_light(3, True)

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
	r = requests.get(config.config.url)
	j =  r.json()
	if j[u'door'] == "open":
		## Always push U-Bahn for now.
		push(station_u, linename_u, destination_u, walking_time_u)
	else:
		set_traffic_light(0)



def push(station, linename, destination, walking_time): # Pushes the Lines to the Display
	lifedata = None
	lifedata = foo.getlivedata(station)
	reduced_lifedata = []

	for entry in lifedata:
		if entry["linename"] == linename and entry["destination"] == destination:
			reduced_lifedata.append(entry)

	dept = reduced_lifedata[0]

	print dept["time"]

	if dept["time"] < walking_time + 2 and dept["time"] > walking_time:
		print "green"
		set_traffic_light(3)
		return 3

	elif dept["time"] <= walking_time and dept["time"] >= walking_time -1:
		print "yellow"
		set_traffic_light(2)
		return 2

	else:
		print "red"
		set_traffic_light(1)
		return 1

# Loop

mqttc.connect(config.host, config.port, 60)

try:
		print("Entered loop")
		# reset all lights to off
		set_single_light(1, False)
		set_single_light(2, False)
		set_single_light(3, False)
		while True:
				refresh()
				time.sleep(10)
except KeyboardInterrupt:
		print 'interrupted!'
		mqttc.disconnect()
