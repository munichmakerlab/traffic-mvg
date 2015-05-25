import paho.mqtt.client as mqtt
import MVGLive
import time
import config
import requests
url = "http://status.munichmakerlab.de/api.php"

topic_red = "mumalab/room/trafficlight/red"
topic_yellow = "mumalab/room/trafficlight/yellow"
topic_green = "mumalab/room/trafficlight/green"

def on_connect(mosq, obj, rc):
	print("Connect with RC " + str(rc))

def on_disconnect(client, userdata, rc):
	print("Disconnected (RC " + str(rc) + ")")

def on_log(client, userdata, level, buf):
	print(buf)

prev = 0

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


def set_single_light(light, state):
	global state_1
	global state_2
	global state_3

	if light == 1 and state_1 != state:
		mqttc.publish(topic_red, int(state), 1, False)
		state_1 = state
	elif light == 2 and state_2 != state:
		mqttc.publish(topic_yellow, int(state), 1, False)
		state_2 = state
	elif light == 3 and state_3 != state:
		mqttc.publish(topic_green, int(state), 1, False)
		state_3 = state

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

def refresh():
	r = requests.get(url)
	j =  r.json()
	if j[u'door'] == "open":
		push_u()
	else:
		set_traffic_light(0)


def push_u(): # Pushes the Lines to the Display
	# TODO: look at http://status.munichmakerlab.de/simple.php

	lifedata = None
	lifedata = foo.getlivedata("Obersendling")
	reduced_lifedata = []

	for entry in lifedata:
		if entry["linename"] == u"U3" and entry["destination"] == u"Moosach":
			reduced_lifedata.append(entry)

	dept = reduced_lifedata[0]

	print dept["time"]

	if dept["time"] < 7 and dept["time"] > 5:
		print "green"
		set_traffic_light(3)
		return 3

	elif dept["time"] <= 5 and dept["time"] >= 4:
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
		set_single_light(1, False)
		set_single_light(2, False)
		set_single_light(3, False)
		while True:
				prev = refresh()
				time.sleep(10)
except KeyboardInterrupt:
		print 'interrupted!'
		mqttc.disconnect()
