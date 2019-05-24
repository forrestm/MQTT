# ! /usr/bin/env python

###################################################################
#
# taken from https://pypi.python.org/pypi/paho-mqtt and edited by
# 	Forrest Montgomery specifically for his MQTT controlled Servo project
# 	April 15, 2015
#
###################################################################


# Define the host for MQTT as a str
# Define the port port MQTT as int
# host = "test.mosquitto.org"
# port = 8080

import paho.mqtt.client as mqtt
host = "iot.eclipse.org"
# Sometimes 80 works better
port = 1883

# host = "broker.mqttdashboard.com"
# port = 8000

# This function takes a value between in_min and in_max and returns a number
# between out_min and out_max. The output is a specific servo value that is
# used to turn the servo with the Adafruit servo libary


def arduino_map(x, in_min, in_max, out_min, out_max):
    """
    This function takes a value between in_min and in_max and returns a number.

    Between out_min and out_max. The output is a specific servo value that is
    used to turn the servo with the Adafruit servo libary
    """
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def on_connect(client, userdata, flags, rc):
    """
    The callback for when the client receives a CONNACK response from the.

    server.
    """
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("CRAWLAB/twoLink")


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    # servo_Small = int(msg.payload[0])
    # servo_Large = int(msg.payload[2])
    # small_servo_angle = arduino_map(servo_Small, -60, 60, 310, 480)
    # large_servo_angle = arduino_map(servo_Large, -35, 35, 410, 514)
    print(msg.topic+" "+str(msg.payload))
    Servos_Tup = eval(msg.payload)
    servo_Small = Servos_Tup[0]
    servo_Large = Servos_Tup[1]
    print "Big Servo is %s" % servo_Large
    print "Small Servo is %s" % servo_Small


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(host, port, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
