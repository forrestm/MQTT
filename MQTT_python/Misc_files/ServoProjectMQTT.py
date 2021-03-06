#! /usr/bin/env python

##########################################################################################
# MQTT_basic.py
#
# Basic implementation of a MQTT client
#
# From: http://eclipse.org/paho/clients/python/
#
# NOTE: Any plotting is set up for output, not viewing on screen.
#       So, it will likely be ugly on screen. The saved PDFs should look
#       better.
#
# Created: 01/14/15
#   - Joshua Vaughan
#   - joshua.vaughan@louisiana.edu
#   - http://www.ucs.louisiana.edu/~jev9637
#
# Modified:
#   *
#
##########################################################################################

import paho.mqtt.client as mqtt
import time
from Adafruit_PWM_Servo_Driver import PWM
 
pwm = PWM(0x40, debug=True)

pwm.setPWMFreq(60)

## Eclipse
HOST = 'iot.eclipse.org'
PORT = 80
USERNAME = None
PASSWORD = None

# MQTT Dashboard
#HOST = 'mqtt.hebeje.be'
#PORT = 3445
#USERNAME = None
#PASSWORD = None

# This function takes a value between in_min and in_max and returns a number between out_min and out_max
# The output is a specific servo value that is used to turn the servo with the Adafruit servo libary
def arduino_map(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
  client.subscribe("CRAWLAB/twoLink")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
  # print(msg.topic + ' Received at: ' + str(time.time()) + ' Sent at: ' + str(msg.payload) + ' Latency: {:0.4f}'.format(time.time() - float(msg.payload)))
  #print(msg.payload)
  servo_Small = int(msg.payload[1])
  servo_Large = int(msg.payload[0])
  small_servo_angle = arduino_map(servo_Small, -60, 60, 410, 514)
  large_servo_angle = arduino_map(servo_Large, -35, 35, 310, 480) 
  print "Big Servo is %s" % servo_Large
  print "Small Servo is %s" % servo_Large
  pwm.setPWM(0, 0, servo_Large)
  time.sleep(1)
  pwm.setPWM(6, 0, servo_Small)
  time.sleep(1)
  
client = mqtt.Client()

# if USERNAME is not None:
 #    client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
  
client.connect(HOST, PORT, 60)
  
  # Blocking call that processes network traffic, dispatches callbacks and
  # handles reconnecting.
  # Other loop*() functions are available that give a threaded interface and a
  # manual interface.
client.loop_forever()


