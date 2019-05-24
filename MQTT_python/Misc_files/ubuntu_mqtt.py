"""
Script to control Polulu Maestro over MQTT.
maestro_servoControl.py

class to control Polulu Maestro USB servo controllers
 https://www.pololu.com/product/1350/
 Initial setup of the Maestro must be completed in Windows or Linux

Modified version of code from:
  http://martinsant.net/?page_id=479


NOTE: Any plotting is set up for output, not viewing on screen.
      So, it will likely be ugly on screen. The saved PDFs should look
      better.

Created: 05/05/15
  - Joshua Vaughan
  - joshua.vaughan@louisiana.edu
  - http://www.ucs.louisiana.edu/~jev9637

Modified:
  * Forrest Montgomery May 13, 2015
    Added mqtt protocol and specific servo data
    And changed the usb address to /dev/ttyACM0

"""

import serial
import paho.mqtt.client as mqtt

# Define the host for MQTT as a str
# Define the port port MQTT as int
# host = "test.mosquitto.org"
# port = 8080


host = "iot.eclipse.org"
port = 1883

# host = "broker.mqttdashboard.com"
# port = 8000


def arduino_map(x, in_min, in_max, out_min, out_max):
    """
    Thi function takes a value between in_min and in_max and returns a number.

    Between out_min and out_max. The output is a specific servo value that is
    used to turn the servo with the Adafruit servo libary
    """
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


class ServoController(object):

    """Class to communicate with a Polulu Maestro USB servo controller."""

    def __init__(self, usbPort):
        self.controller = serial.Serial(usbPort, baudrate=19200, timeout=1)

    def closeServo(self):
        self.controller.close()

    def setAngle(self, channel, angle):
        """
        Set the angle of the servo.

        Actually uses the Mini SSC protocol command for setTarget

        Arguments:
          channel : the channel of the servo to set
          angle : the angle to move to in degrees, must be between 0 and 180

        Returns:
          nothing
        """
        if angle > 180 or angle < 0:
            print 'Angle outside of acceptable range. Setting to 90deg'
            angle = 90

        # Convert the angle to the correct target command 0-255, 128 center
        byteone = int(254 * angle / 180)

        # for the command and send it
        setAngle_command = chr(0xFF) + chr(channel) + chr(byteone)
        self.controller.write(setAngle_command)

    def setTarget(self, servo, target):
        """
        Get the "raw" target pulse length (which determines desired position).

        From the manual - "The target represents the pulse width to transmit
                           in units of quarter- microseconds"

        A target of 1500 is centered for most servos

        Arguments:
          servo : the servo to set position of
          position : raw pulse-width of the servo, 1000-2000, 1500 is center

        Returns:
          nothing
        """
        # account for 1/4-microsecond scaling
        target = target * 4

        # break target value into high and low bytes
        target_lowByte = (target & 0x7f)
        target_highByte = (target >> 7) & 0x7f

        # make sure channel is a byte
        chan = servo & 0x7f

        # form the data packet to send and send it
        data = chr(0xaa) + chr(0x0c) + chr(0x04) + chr(chan) + chr(
               target_lowByte) + chr(target_highByte)
        self.controller.write(data)

    def getPosition(self, servo):
        """
        Get the "raw" position of the servo.

        Arguments:
          servo : the servo to get position of

        Returns:
          TODO: figure out exactly what's being returned
                05/06/15 - JEV - joshua.vaughan@louisiana.edu
        """
        # make sure channel is a byte
        chan = servo & 0x7f

        # for the getPosition request and send it
        data = chr(0xaa) + chr(0x0c) + chr(0x10) + chr(chan)
        self.controller.write(data)

        w1 = ord(self.controller.read())
        w2 = ord(self.controller.read())

        return w1, w2

    def getErrors(self):

        data = chr(0xaa) + chr(0x0c) + chr(0x21)
        self.controller.write(data)

        if self.controller.read() != '':
            w1 = ord(self.controller.read())
            w2 = ord(self.controller.read())
        else:
            w1 = None
            w2 = None

        return w1, w2

    def triggerScript(self, subNumber):
        """Trigger an internal script on the device."""
        data = chr(0xaa) + chr(0x0c) + chr(0x27) + chr(0)
        self.controller.write(data)


if __name__ == '__main__':

    # Define the system parameters
    # PORT = '/dev/tty.usbmodem00110371'
    PORT = '/dev/ttyACM0'
    CHANNEL_Big = 1
    CHANNEL_Small = 0

    # Set up the servoController object
    servoControl = ServoController(PORT)

    # The callback for when the client receives a CONNACK response from the
    # server.
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("CRAWLAB/twoLink")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        # servo_Small = int(msg.payload[0])
        # servo_Large = int(msg.payload[2])
        print(msg.topic+" "+str(msg.payload))
        Servos_Tup = eval(msg.payload)
        servo_Small = Servos_Tup[1]
        servo_Large = Servos_Tup[0]
        small_servo_angle = arduino_map(servo_Small, 60, -60, 1050, 1700)
        large_servo_angle = arduino_map(servo_Large, 30, -30, 1200, 1800)
        print "Big Servo is %s" % servo_Large
        print "Small Servo is %s" % servo_Small
        servoControl.setTarget(CHANNEL_Small, small_servo_angle)
        servoControl.setTarget(CHANNEL_Big, large_servo_angle)

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
