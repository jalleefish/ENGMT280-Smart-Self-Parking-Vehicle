import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while True:
    success, bgr = cap.read()
    width = int(cap.get(3))  # Get the width of the frame
    height = int(cap.get(4))  # Get the height of the frame

    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    
    lowerBlue = np.array([90, 100, 50])
    upperBlue = np.array([135, 255, 255])
    lowerReg = np.array([0, 150, 50])
    upperRed = np.array([10, 255, 255])
    lowerYellow = np.array([20, 100, 100])
    upperYellow = np.array([35, 255, 255])
    
    blue = cv2.inRange(hsv, lowerBlue, upperBlue)
    red = cv2.inRange(hsv, lowerReg, upperRed)
    yellow = cv2.inRange(hsv, lowerYellow, upperYellow)

    blueMask = cv2.bitwise_and(bgr, bgr, mask=blue)
    redMask = cv2.bitwise_and(bgr, bgr, mask=red)
    yellowMask = cv2.bitwise_and(bgr, bgr, mask=yellow)
    
    blueContours, blueHierarchy=cv2.findContours(blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    redContours, redHierarchy=cv2.findContours(red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    yellowContours, yellowHierarchy=cv2.findContours(yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(blueContours) != 0:
        for blueContour in blueContours:
            if cv2.contourArea(blueContour) > 500:
                x, y, w, h = cv2.boundingRect(blueContour)
                cv2.rectangle(bgr, (x, y), (x + w, y + h), (255, 0, 0), 2)
                
    if len(redContours) != 0:
        for redContour in redContours:
            if cv2.contourArea(redContour) > 500:
                x, y, w, h = cv2.boundingRect(redContour)
                cv2.rectangle(bgr, (x, y), (x + w, y + h), (0, 0, 255), 2)
                
    if len(yellowContours) != 0:
        for yellowContour in yellowContours:
            if cv2.contourArea(yellowContour) > 500:
                x, y, w, h = cv2.boundingRect(yellowContour)
                cv2.rectangle(bgr, (x, y), (x + w, y + h), (0, 255, 255), 2)
                
    
    cv2.imshow('Original', bgr)
    cv2.imshow('Blue Only', blue)
    cv2.imshow('Red Only', red)
    cv2.imshow('Yellow Only', yellow)
    cv2.imshow('Blue Mask', blueMask)
    cv2.imshow('Red Mask', redMask)
    cv2.imshow('Yellow Mask', yellowMask)
    
    # Wait 1ms and check for 'q' key to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()