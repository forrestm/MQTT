#! /usr/bin/env python

###############################################################################
# maestro_servoControl.py
#
# class to control Polulu Maestro USB servo controllers
#  https://www.pololu.com/product/1350/
#  Initial setup of the Maestro must be completed in Windows or Linux
#
# Modified version of code from:
#   http://martinsant.net/?page_id=479
#
#
# NOTE: Any plotting is set up for output, not viewing on screen.
#       So, it will likely be ugly on screen. The saved PDFs should look
#       better.
#
# Created: 05/05/15
#   - Joshua Vaughan
#   - joshua.vaughan@louisiana.edu
#   - http://www.ucs.louisiana.edu/~jev9637
#
# Modified:
#   * Forrest Montgomery May 13, 2015
#     Added mqtt protocol and specific servo data
#     And changed the usb address to /dev/ttyACM0
#
###############################################################################

import serial
import time
import paho.mqtt.client as mqtt
import cv2_color_track as track
import os

# Define the host for MQTT as a str
# Define the port port MQTT as int
# host = "test.mosquitto.org"
# port = 8080


host = "iot.eclipse.org"
port = 1883

# host = "broker.mqttdashboard.com"
# port = 8000

if __name__ == '__main__':


    # The callback for when the client receives a CONNACK response from the
    # server.
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("CRAWLAB/twoLink/opencv/email")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        # servo_Small = int(msg.payload[0])
        # servo_Large = int(msg.payload[2])
        # print(msg.topic+" "+str(msg.payload))
        topic = str(msg.topic)
        print topic
        payload = str(msg.payload)
        email = payload
        print email
        os.system('sudo python cv2_color_track.py %s' % email)
        # payload = str(msg.payload)
        # if payload == 'on':
        #     os.system('sudo python cv2_color_track.py %s' % email)



        # if topic == "CRAWLAB/twoLink/opencv/email":
        #     email = str(msg.payload)
        # if topic == "CRAWLAB/twoLink/opencv":
        #     on_or_off = str(msg.payload)
        #     print on_or_off
        #     if on_or_off == 'on':
        #         os.system('sudo python cv2_color_track.py %s' % email)
                


        # Servos_Tup = eval(msg.payload)
        # servo_Small = Servos_Tup[1]
        # servo_Large = Servos_Tup[0]
        # small_servo_angle = arduino_map(servo_Small, 60, -60, 1050, 1700)
        # large_servo_angle = arduino_map(servo_Large, 30, -30, 1200, 1800)
        # print "Big Servo is %s" % servo_Large
        # print "Small Servo is %s" % servo_Small
        # servoControl.setTarget(CHANNEL_Small, small_servo_angle)
        # servoControl.setTarget(CHANNEL_Big, large_servo_angle)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(host, port, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and
    # a manual interface.
    client.loop_forever()

    # try:
    #     while True:
    #         angle = raw_input("Angle (0 to 180 x to exit):")

    #         if angle == 'x':
    #             servoControl.closeServo()
    #             break
    #         elif int(angle) < 0 or int(angle) > 180:
    #             print 'Please enter an angle between 0 and 180.'
    #         else:
    #             servoControl.setAngle(CHANNEL, int(angle))

    # except KeyboardInterrupt:
    #     servoControl.closeServo()
