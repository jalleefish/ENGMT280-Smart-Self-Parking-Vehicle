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
        
    success, bgr = cap.read()
    width = int(cap.get(3))  # Get the width of the frame
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
                
    if len(greenContours) != 0:
        for greenContour in greenContours:
            if cv2.contourArea(greenContour) > 500:
                x, y, w, h = cv2.boundingRect(greenContour)
                cv2.rectangle(bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
    if len(yellowContours) != 0:
        for yellowContour in yellowContours:
            if cv2.contourArea(yellowContour) > 500:
                x, y, w, h = cv2.boundingRect(yellowContour)
                cv2.rectangle(bgr, (x, y), (x + w, y + h), (0, 255, 255), 2)
                
    if len(redContours) != 0:
        for redContour in redContours:
            if cv2.contourArea(redContour) > 500:
                x, y, w, h = cv2.boundingRect(redContour)
                cv2.rectangle(bgr, (x, y), (x + w, y + h), (0, 0, 255), 2)
                
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
    if sender == 'colourScan':
        colourScan = True
    if sender == 'noScan':
        colourScan == False
    if colourTarget.count(1) >= 2:
        colourScan = False
        break
    
    if colourScan:
        # RED
        maskR = Image.fromarray(maskRed)
        boundsR = maskR.getbbox()

        # if red
        if not(boundsR == None):
            xr1, yr1, xr2, yr2 = boundsR
            if (xr1 - xr2) > boundLenX and (yr2 - yr1) > boundLenY and yr1 > boundLowY:
                redBool = 1
                averageR = (xr1 - xr2)/2 + xr1
                if averageR < (averagesR[-1] - colourError):
                    print('new red')
                    colours.append(0)
                    if colourTarget[0]:
                        redTarget = True
                if redTarget:
                    if xr1 > targetColourPos:
                        target = True
                        colourPos.append(xr1)
                        redTarget = False
                averagesR.append(averageR)
                if colourTarget.count(1) < 2:
                    colourTarget[0] = 1
        else:
            redBool = 0
        
        # YELLOW
        maskY = Image.fromarray(maskYellow)
        boundsY = maskY.getbbox()

        # if yellow
        if not(boundsY == None):
            xy1, yy1, xy2, yy2 = boundsY
            if (xy1 - xy2) > boundLenX and (yy2 - yy1) > boundLenY and yy1 > boundLowY:
                yellowBool = 1
                averageY = (xy1 - xy2)/2 + xy1
                if averageY < (averagesY[-1] - colourError):
                    print('new yellow')
                    colours.append(1)
                    if colourTarget[1]:
                        yellowTarget = True
                if yellowTarget:
                    if xy1 > targetColourPos:
                        target = True
                        colourPos.append(xy1)
                        yellowTarget = False
                averagesY.append(averageY)
                if colourTarget.count(1) < 2:
                    colourTarget[1] = 1
        else:
            yellowBool = 0

        # GREEN
        maskG = Image.fromarray(maskGreen)
        boundsG = maskG.getbbox()

        # if green
        if not(boundsG == None):
            xg1, yg1, xg2, yg2 = boundsG
            if (xg1 - xg2) > boundLenX and (yg2 - yg1) > boundLenY and yg1 > boundLowY:
                greenBool = 1
                averageG = (xg1 - xg2)/2 + xg1
                if averageG < (averagesG[-1] - colourError):
                    print('new green')
                    colours.append(2)
                    if colourTarget[2]:
                        greenTarget = True
                if greenTarget:
                    if xg1 > targetColourPos:
                        target = True
                        colourPos.append(xg1)
                        greenTarget = False
                averagesG.append(averageG)
                if colourTarget.count(1) < 2:
                    colourTarget[2] = 1
        else:
            greenBool = 0
        
        # BLUE
        maskB = Image.fromarray(maskBlue)
        boundsB = maskB.getbbox()

        # if blue
        if not(boundsB == None):
            xb1, yb1, xb2, yb2 = boundsB
            if (xb1 - xb2) > boundLenX and (yb2 - yb1) > boundLenY and yb1 > boundLowY:
                blueBool = 1
                averageB = (xb1 - xb2)/2 + xb1
                if averageB < (averagesB[-1] - colourError):
                    print('new blue')
                    colours.append(3)
                    if colourTarget[3]:
                        blueTarget = True
                if blueTarget:
                    if xb1 > targetColourPos:
                        target = True
                        colourPos.append(xb1)
                        blueTarget = False
                averagesB.append(averageB)
                if colourTarget.count(1) < 2:
                    colourTarget[3] = 1
        else:
            blueBool = 0
        
    if target:
        conn.sendall("saveDistance".encode())
        target = False

    # Wait 1ms and check for 'q' key to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()