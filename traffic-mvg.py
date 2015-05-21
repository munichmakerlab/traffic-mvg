import paho.mqtt.client as mqtt
import MVGLive
import time
import config

topic_red = "mumalab/room/trafficlight/red"
topic_yellow = "mumalab/room/trafficlight/yellow"
topic_green = "mumalab/room/trafficlight/green"

def on_connect(mosq, obj, rc):
	print("Connect with RC " + str(rc))

def on_disconnect(client, userdata, rc):
	print("Disconnected (RC " + str(rc) + ")")

def on_log(client, userdata, level, buf):
	print(buf)


mqttc = mqtt.Client("")
mqttc.username_pw_set(config.username, config.password)
mqttc.connect(config.host, config.port, 60)
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_log = on_log

foo = MVGLive.MVGLive()

def set_single_light(light, state):
	if light == 1:
		mqttc.publish(topic_red, int(state), 1, False)
	elif light == 2:
		mqttc.publish(topic_yellow, int(state), 1, False)
	elif light == 3:
		mqttc.publish(topic_green, int(state), 1, False)

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


def refresh(): # Pushes the Lines to the Display
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

	elif dept["time"] <= 5 and dept["time"] >= 4:
		print "yellow"
		set_traffic_light(2)

	else:
		print "red"
		set_traffic_light(1)

# Loop

try:
		print("Entered loop")
		while True:
				refresh()
				time.sleep(10)
except KeyboardInterrupt:
		print 'interrupted!'
