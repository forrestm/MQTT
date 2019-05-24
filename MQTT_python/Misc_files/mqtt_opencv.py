"""
Script to initiate an OpenCV Script when issued by an MQTT message.

Taken from https://pypi.python.org/pypi/paho-mqtt and edited by
Forrest Montgomery specifically for his MQTT controlled Servo project
July 15, 2015
"""

import paho.mqtt.client as mqtt
import time
# Define the host for MQTT as a str
# Define the port MQTT as int

# Different host choices

# host = "test.mosquitto.org"
# port = 8080

# host = "broker.mqttdashboard.com"
# port = 8000

host = "iot.eclipse.org"
port = 1883

username = None
password = None

topic1 = 'CRAWLAB/twoLink/opencv'
topic2 = 'CRAWLAB/twoLink/opencv/email'


def on_connect(client, userdata, flags, rc):
    """
    The callback for when the client receives a CONNACK response from the.

    server.
    """
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic1)
    client.subscribe(topic2)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    message = msg.payload
    topic = msg.topic
    if topic == "CRAWLAB/twoLink/opencv":
        if message == 'on':



client = mqtt.Client()

if username is not None:
    client.username_pw_set(username, password)

client.on_connect = on_connect
client.on_message = on_message

client.connect(host, port, 60)

# Non-blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
client.loop_start()

# This loop will run printing the kernel time while also reading MQTT data
try:
    while True:
        # print time.time()
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    client.loop_stop()
