import cv2
import numpy as np
from PIL import Image
import time
import socket
import json

HOST = "0.0.0.0"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print("Waiting for ESP32...")
conn, addr = server_socket.accept()
print(f"Connected by {addr}")

buffer = ""

url = 0
# url = "http://192.168.137.249:81/stream"
cap = cv2.VideoCapture(url)  # Open the ESP32-CAM stream

# Define color ranges for blue, red, and yellow in HSV
lowerBlue = np.array([90, 100, 50])
upperBlue = np.array([135, 255, 255])
lowerGreen = np.array([40, 70, 50])
upperGreen = np.array([80, 255, 255])
lowerYellow = np.array([20, 70, 100])
upperYellow = np.array([35, 255, 255])
lowerRed = np.array([0, 100, 50])
upperRed = np.array([10, 255, 255])
lowerRed2 = np.array([160, 100, 50])
upperRed2 = np.array([180, 255, 255])

boundLenY = 60
boundLenX = 30
boundLowY = 200

# sensor stuff
colourCheck = 1
colourTarget = [0, 0, 0, 0]
coloursFound = 0
orderedColours = []
colours = []
colourPos = []
averagesR = [200]
averagesY = [200]
averagesG = [200]
averagesB = [200]
blueTarget = False
redTarget = False
greenTarget = False
yellowTarget = False
target = 0
targetPos = []
colourError = 10
targetColourPos = 20
run = True
sender = ''
receiver = ''
colourScan = True
targetNumbers = []
firstTarget = -1
secondTarget = -1

while True:
    data = conn.recv(1024).decode()
    if not data:
        break
    buffer += data

    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        line = line.strip()
        if not line:
            continue
        sender = line
    
    if sender == 'colourScan':
        colourScan = True
    if sender == 'noScan':
        colourScan == False
    if colourTarget.count(1) >= 2:
        colourScan = False
        break
    
    if colourScan:
        url = 0
        # url = "http://192.168.137.249:81/stream"
        cap = cv2.VideoCapture(url)  # Open the ESP32-CAM stream
        
        success, bgr = cap.read()
        width = int(cap.get(3))  # Get the width of the frame
        centre = width/2
        height = int(cap.get(4))  # Get the height of the frame

        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        
        # Create ranges for each color
        blue = cv2.inRange(hsv, lowerBlue, upperBlue)
        green = cv2.inRange(hsv, lowerGreen, upperGreen)
        yellow = cv2.inRange(hsv, lowerYellow, upperYellow)
        red1 = cv2.inRange(hsv, lowerRed, upperRed)
        red2 = cv2.inRange(hsv, lowerRed2, upperRed2)
        red = red1 + red2  # Combine the two red masks

        # Create masks for each color
        maskBlue = cv2.bitwise_and(bgr, bgr, mask=blue)
        maskGreen = cv2.bitwise_and(bgr, bgr, mask=green)
        maskYellow = cv2.bitwise_and(bgr, bgr, mask=yellow)
        maskRed = cv2.bitwise_and(bgr, bgr, mask=red)
        
        # Find contours for each color mask
        blueContours, blueHierarchy=cv2.findContours(blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        greenContours, greenHierarchy=cv2.findContours(green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        yellowContours, yellowHierarchy=cv2.findContours(yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        redContours, redHierarchy=cv2.findContours(red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw rectangles around detected contours
        if len(blueContours) != 0:
            for blueContour in blueContours:
                if cv2.contourArea(blueContour) > 500:
                    x, y, w, h = cv2.boundingRect(blueContour)
                    cv2.rectangle(bgr, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    colour = [3, x, y, w, h]
                    colours.append(colour)
                    
        if len(greenContours) != 0:
            for greenContour in greenContours:
                if cv2.contourArea(greenContour) > 500:
                    x, y, w, h = cv2.boundingRect(greenContour)
                    cv2.rectangle(bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    colour = [2, x, y, w, h]
                    colours.append(colour)
                    
        if len(yellowContours) != 0:
            for yellowContour in yellowContours:
                if cv2.contourArea(yellowContour) > 500:
                    x, y, w, h = cv2.boundingRect(yellowContour)
                    cv2.rectangle(bgr, (x, y), (x + w, y + h), (0, 255, 255), 2)
                    colour = [1, x, y, w, h]
                    colours.append(colour)
                    
        if len(redContours) != 0:
            for redContour in redContours:
                if cv2.contourArea(redContour) > 500:
                    x, y, w, h = cv2.boundingRect(redContour)
                    cv2.rectangle(bgr, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    colour = [0, x, y, w, h]
                    colours.append(colour)
                    
        # Display the processed images
        cv2.imshow('Original', bgr)
        #cv2.imshow('Blue Only', blue)
        #.imshow('Green Only', green)
        #.imshow('Yellow Only', yellow)
        #cv2.imshow('Red Only', red)

        # cv2.imshow('Blue Mask', blueMask)
        # cv2.imshow('Green Mask', greenMask)
        # cv2.imshow('Yellow Mask', yellowMask)
        # cv2.imshow('Red Mask', redMask)

        # RED
        coloursAve = []
        while not(colours == []):
            for i in range(0, len(colours)):
                ave = colours[1] + colours[3]/2
                coloursAve.append(ave)

            closest_value = coloursAve[1]
            min_diff = abs(coloursAve[1] - centre)

            for value in coloursAve:
                current_diff = abs(value - centre)
                if current_diff < min_diff:
                    min_diff = current_diff
                    closest_value = value
            ColourIndex = coloursAve.index(closest_value)
            orderedColours.append(colours[ColourIndex])
            colours = []
            print(orderedColours[-1])
        if len(orderedColours) > 2:
            for i in range(2, len(orderedColours)):
                if (i - 2) not in targetNumbers:
                    if orderedColours[i][0] == orderedColours[0][0] or orderedColours[i][0] == orderedColours[1][0]:
                        if len(targetNumbers) < 2:
                            targetNumbers.append(i - 2)
        
    if len(targetNumbers) >= 1:
        firstTarget = targetNumbers[0]
        conn.sendall(firstTarget.encode())
    if len(targetNumbers) == 2:
        secondTarget = targetNumbers[1]
        conn.sendall(secondTarget.encode())
        colourScan = False

    # Wait 1ms and check for 'q' key to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()