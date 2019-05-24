#!/usr/bin/env python

"""
Written by Forrest Montgomery, with help from Dr. Vaughan.

This program tracks two different colored objects, then spits out a graph and
a csv file of the postions of the objects. It will soon email the data to the
user of the accompanying website.
"""

import cv2
import numpy as np
from time import strftime
import time
import matplotlib.pyplot as plt
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.text import MIMEText
import os
from email.mime.base import MIMEBase
from sys import argv

try:
    email = argv[1]
except IndexError:
    email = 'null'
print email

save_data = True
# time for the program to run
kill_time = 20

if save_data:
    # names the output file as the date and time that the program is run
    filename_blue = strftime("%m_%d_%Y_%H%M") + "_blue"
    filename_orange = strftime("%m_%d_%Y_%H%M") + "_orange"
    # gives the path of the file to be opened
    filepath_orange = filename_orange + ".csv"
    filepath_blue = filename_blue + ".csv"

t0 = time.time()
class ColorTracker:

    def __init__(self):
        # Creates a window that can be used as a placeholder for images and
        # trackbars
        cv2.namedWindow("ColourTrackerWindow", cv2.CV_WINDOW_AUTOSIZE)
        cv2.namedWindow("ColourTrackerWindow2", cv2.CV_WINDOW_AUTOSIZE)
        # A class that captures video. The number is the id of the opened
        # video capturing device 0 is for the default device
        self.capture = cv2.VideoCapture(0)

    def run(self):
        # sets the inital time
        inital_Time = time.time()
        # Alots a zero numpy array to data, for storing the motion later
        data = np.zeros((1, 3))
        data2 = np.zeros((1, 3))

        while True:
            f, img = self.capture.read()
            # Just the raw footage from the camera
            original_image = img
            # Displays the raw footage
            cv2.imshow("ColourTrackerWindow", original_image)
            # Applies a Gassian Blur to the image
            img = cv2.GaussianBlur(img, (5, 5), 0)
            # Converts the color of the image to HSV colorspace
            img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            # displays the img in the window defined by namedWindow
            cv2.imshow("ColourTrackerWindow", img)
            # Lower HSV color limit

            # try blue
            color2_lower = np.array([64, 113, 0], np.uint8)

            # try blue
            color2_upper = np.array([179, 255, 199], np.uint8)

            # try orange
            # color_lower = np.array([24, 81, 214], np.uint8)
            color_lower = np.array([0, 84, 0], np.uint8)
            # Upper HSV color limit

            # try orange
            color_upper = np.array([46, 255, 255], np.uint8)

            # Checks if array elements lie between the elements of two other
            # arrays

            thresholded_img_2 = cv2.inRange(img, color2_lower, color2_upper)

            thresholded_img = cv2.inRange(img, color_lower, color_upper)

            # This displays the theresholded image
            cv2.imshow("ColourTrackerWindow", thresholded_img)
            cv2.imshow("ColourTrackerWindow2", thresholded_img_2)
            moments = cv2.moments(thresholded_img)
            moments2 = cv2.moments(thresholded_img_2)
            area = moments['m00']
            area2 = moments2['m00']

            # there can be noise in the video so ignore objects with small
            # areas
            if (area > 100000) and (area2 > 100000):
                # determine the x and y coordinates of the center of the object
                # we are tracking by dividing the 1, 0 and 0, 1 moments by the
                # area
                x = moments['m10'] / area
                y = moments['m01'] / area
                x2 = moments2['m10'] / area2
                y2 = moments2['m01'] / area2

                if save_data:
                    # Save the current time and pixel location into the data
                    # array
                    add = np.asarray([[time.time() - inital_Time, x, y]])
                    add2 = np.asarray([[time.time() - inital_Time, x2, y2]])
                    data = np.append(data, add, 0)
                    data2 = np.append(data2, add2, 0)

                # convert center location to integers
                x = int(x)
                y = int(y)
                x2 = int(x2)
                y2 = int(y2)
                t1 = time.time()

                # Create an overlay to mark the center of the tracked object
                # img_shape = cv2.imread('img')
                # height, width, depth = img.shape
                # overlay = np.zeros((height, width, 3), np.uint8)

                # cv2.circle(overlay, (x, y), 2, (0, 0, 0), 20)
                # cv2.add(img, overlay, img)

                # img = cv2.merge(thresholded_img)

            # cv2.imshow("ColourTrackerWindow", img)
            check = cv2.waitKey(20)
            # This closes all the windows and shuts down the camera
            # if check == 1048603 or check == 'ESC':
            total_time = t1 - t0

            if total_time >= kill_time:
                if save_data:
                    # save the data file as comma separated values
                    # remove the first row
                    data = np.delete(data, 0, 0)
                    data2 = np.delete(data2, 0, 0)
                    full_data = np.hstack((data, data2))
                    # Removing second time column
                    full_data = np.delete(full_data,3 ,1)
                    np.savetxt(filepath_orange, full_data, delimiter=",", header="Time \
                    # # (s), X Position Orange(pixels), Y Position Orange(pixels), X Position Blue(pixels), Y Position Blue(pixels)")
                    # np.savetxt(filepath_orange, data, delimiter=",", header="Time(orange) \
                    # # (s), X Position(pixels), Y Position(pixels)")
                    # np.savetxt(filepath_blue, data2, delimiter=",", header="Time(blue) \
                    # # (s), X Position(pixels), Y Position(pixels)")
                    x = data[:, 1]
                    # I flipped the camera so the negative is needed to make
                    # the graph look as if you are looking down.
                    y = np.negative(data[:, 2])
                    x2 = data2[:, 1]
                    y2 = np.negative(data2[:, 2])
                    print data
                    print data2

                    # Found most ofthis at http://ryrobes.com/python/python-snippet-sending-html-email-with-an-attachment-via-google-apps-smtp-or-gmail/
                    # Adapted to accept a list of files for multiple file attachments
                    # From other stuff I googled, a little more elegant way of converting html to plain text
                    # This works in 2.7 and my brain gets it.

                    ######### Email Stuff #######################################

                    emailfrom = "mqttarm@gmail.com"
                    emailto = email
                    fileName = filepath_orange
                    username = "mqttarm"
                    password = "q2w3e4r5t6y7u8i9o0p"

                    msg = MIMEMultipart()
                    msg["From"] = emailfrom
                    msg["To"] = emailto
                    msg["Subject"] = "Here is your data!"
                    msg.preamble = "This is a test of the Servo Arm"

                    with open(fileName,'r') as fp:
                        attachment = MIMEBase('application','octet-stream')
                        attachment.set_payload(fp.read())
                        encoders.encode_base64(attachment)
                        attachment.add_header('Content-Disposition','attachment',filename=os.path.split(fileName)[1])
                        msg.attach(attachment)

                    server = smtplib.SMTP("smtp.gmail.com:587")
                    server.starttls()
                    server.login(username, password)
                    server.sendmail(emailfrom, emailto, msg.as_string())
                    server.quit()

                #     plt.figure(1)
                #     plt.subplot(211)
                #     plt.axis([0, 650, -450, 0])
                #     plt.title('Orange')
                #     plt.scatter(x, y)
                #     plt.subplot(212)
                #     plt.axis([0, 650, -250, 0])
                #     plt.title('Blue')
                #     plt.scatter(x2, y2)
                #     plt.show()

                cv2.destroyWindow("ColourTrackerWindow")
                cv2.destroyWindow("ColourTrackerWindow2")
                self.capture.release()
                break

if __name__ == "__main__":
    color_tracker = ColorTracker()
    color_tracker.run()
