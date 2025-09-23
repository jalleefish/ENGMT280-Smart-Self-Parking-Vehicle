import cv2
import numpy as np

url = 0
#url = "http://192.168.137.61:81/stream"
cap = cv2.VideoCapture(url)  # Open the ESP32-CAM stream

while True:
    success, bgr = cap.read()
    width = int(cap.get(3))  # Get the width of the frame
    height = int(cap.get(4))  # Get the height of the frame

    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    
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
    
<<<<<<< Updated upstream:System Logic/Drafts/imageProcessing.py
    # Create ranges for each color
=======
    
    # Create masks for each color
>>>>>>> Stashed changes:Image Processing Code/imageProcessing.py
    blue = cv2.inRange(hsv, lowerBlue, upperBlue)
    green = cv2.inRange(hsv, lowerGreen, upperGreen)
    yellow = cv2.inRange(hsv, lowerYellow, upperYellow)
    red1 = cv2.inRange(hsv, lowerRed, upperRed)
    red2 = cv2.inRange(hsv, lowerRed2, upperRed2)
    red = red1 + red2  # Combine the two red masks

    # Create masks for each color
    blueMask = cv2.bitwise_and(bgr, bgr, mask=blue)
    greenMask = cv2.bitwise_and(bgr, bgr, mask=green)
    yellowMask = cv2.bitwise_and(bgr, bgr, mask=yellow)
    redMask = cv2.bitwise_and(bgr, bgr, mask=red)
    
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
<<<<<<< Updated upstream:System Logic/Drafts/imageProcessing.py
    # cv2.imshow('Original', bgr)
=======
    cv2.imshow('Original', bgr)
>>>>>>> Stashed changes:Image Processing Code/imageProcessing.py
    #cv2.imshow('Blue Only', blue)
    #.imshow('Green Only', green)
    #.imshow('Yellow Only', yellow)
    #cv2.imshow('Red Only', red)

<<<<<<< Updated upstream:System Logic/Drafts/imageProcessing.py
    # cv2.imshow('Blue Mask', blueMask)
    # cv2.imshow('Green Mask', greenMask)
    # cv2.imshow('Yellow Mask', yellowMask)
    # cv2.imshow('Red Mask', redMask)
=======
    cv2.imshow('Blue Mask', blueMask)
    cv2.imshow('Green Mask', greenMask)
    cv2.imshow('Yellow Mask', yellowMask)
    cv2.imshow('Red Mask', redMask)
>>>>>>> Stashed changes:Image Processing Code/imageProcessing.py

    # Wait 1ms and check for 'q' key to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()