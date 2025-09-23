#actual real car logic
import numpy as np
import cv2
from PIL import Image

# colour recog stuff
red = np.array([[170, 120, 100], [180, 255, 255], [0, 120, 100], [5, 255, 255]])
yellow = np.array([[20, 130, 100], [35, 255, 255]])
green = np.array([[35, 130, 100], [75, 255, 255]])
blue = np.array([[110, 130, 100], [130, 255, 255]])

cam = cv2.VideoCapture(0)

boundLenY = 60
boundLenX = 30
boundLowY = 200

# 2 sections
firstPark = 1
secondPark = 0

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
target = 0
targetPos = []
straightning = []

# states
go = 1
parking = 0
reversing = 0
colourScan = 1
steering = 0
sensorScan = 1
straight = 1
leavePark = 0
run = 1
tryStraight = False
wait = False
waitArray = []

# variables and adjustments
adjustAngle = 5
maxAngle = 26
sensorVariance = 10
wallBuffer = 10
colourError = 10
targetColourPos = 20
straightAdj = 3
parkDist = 30
distFromTarget = 200
waitLength = 10000

# sensor inputs (sensor data number)
sd1 = 0
sd2 = 0
sd3 = 0
sd4 = 0
sd5 = 0
sensorArray = [sd1, sd2, sd3, sd4, sd5]

# outputs
turnAngle = 0 # degrees
motor = 1 # on = 1, off = 0, reverse = -1


while run:
    while wait:
        waitArray.append(1)
        if len(waitArray) > waitLength:
            wait = False

    # STRAIGHT CORRECTIONS

    if straight:
        if abs(sd4 - sd5) > sensorVariance:
            if sd4 > sd5:
                turnAngle = -adjustAngle
            else:
                turnAngle = adjustAngle
        else: 
            turnAngle = 0

    # MOTOR RUNNING AND EMERGENCY STOP

    if go:
        if any(x < wallBuffer for x in sensorArray):
            go = 0
            motor = 0
            break
        elif reversing:
            motor = -1
        else:
            motor = 1
    
    # COLOUR SHIT
    if len(colourPos) > 1:
        colourScan = False

    if colourScan:
        success, bgrImg = cam.read()
        if success:
            hsvImg = cv2.cvtColor(bgrImg, cv2.COLOR_RGB2HSV)
            maskbox = cv2.inRange(hsvImg, (0,0,0), (180,255,255))
            maskbox[605:670, 0:1280] = 255
            display = cv2.bitwise_and(bgrImg, bgrImg, mask = maskbox)

            maskRed = cv2.inRange(cv2.cvtColor(display, cv2.COLOR_BGR2HSV), red[0], red[1])
            maskYellow = cv2.inRange(cv2.cvtColor(display, cv2.COLOR_BGR2HSV), yellow[0], yellow[1])
            maskGreen = cv2.inRange(cv2.cvtColor(display, cv2.COLOR_BGR2HSV), green[0], green[1])
            maskBlue = cv2.inRange(cv2.cvtColor(display, cv2.COLOR_BGR2HSV), blue[0], blue[1])
            maskTemp = cv2.inRange(cv2.cvtColor(display, cv2.COLOR_BGR2HSV), red[2], red[3])
            maskRed = maskRed + maskTemp
            img = bgrImg

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

        else:
            print("no cam")

        # END of colour shit

        # see if there's a target
        if target:
            targetPos.append((sd4 + sd5)/2)
        
        # PARK 1
        if firstPark:
            if not reversing and not steering and not leavePark:
                colourScan = True
            if not(target):
                parking = True
                target = False
            
            if steering:
                steeringAngleDeg = maxAngle

                if abs(sd4 - sd5) > sensorVariance * 3:
                    tryStraight = True

                if abs(sd4 - sd5) < sensorVariance and tryStraight:
                    """ straightning.append(1)
                else:
                    straightning = []
                if len(straightning) > straightAdj: """
                    tryStraight = False
                    straight = True
                    turnAngle = 0
                    steering = False
                    if parking and reversing and not(leavePark):
                        turnPos = (sd4 + sd5)/2
                    if leavePark:
                        colourScan = True
                        leavePark = False
                        secondPark = True
                        firstPark = False
                    
            else:
                turnAngle = 0

            if parking:
                if reversing:
                    if ((sd4 + sd5)/2 <= parkDist):
                        motor = 0
                        reversing = False
                        go = False
                        parking = False
                        wait = True
                        steering = False
                        leavePark = True
                        # remove target
                        target = 0
                    else:
                        motor = -1
                        
                else:
                    if ((sd4 + sd5)/2 - distFromTarget - targetPos[0]) > 0 and parking:
                        reversing = True
                        motor = -1
                        steering = True
                        turnAngle = maxAngle
                        colourScan = False

            if leavePark:
                if (np.isclose(turnPos, (sd4 + sd5)/2, atol = 10)):
                    steering = True
                    turnAngle = maxAngle

        # PARK 2
        if secondPark:
            if len(colourPos) > 1:
                target = True

            if target:
                parking = True
            
            if not parking:
                colourScan = True
            
            if steering:
                steeringAngleDeg = maxAngle

                if abs(sd4 - sd5) > sensorVariance * 3:
                    tryStraight = True

                if abs(sd4 - sd5) < sensorVariance and tryStraight:
                    """ straightning.append(1)
                else:
                    straightning = []
                if len(straightning) > straightAdj: """
                    tryStraight = False
                    straight = True
                    turnAngle = 0
                    steering = False                   
            else:
                turnAngle = 0

            if parking:
                if reversing:
                    if ((sd4 + sd5)/2 <= parkDist):
                        motor = 0
                        reversing = False
                        go = False
                        parking = False
                        steering = False
                        # remove target
                        target = 0
                        break
                    else:
                        motor = -1
                        
                else:
                    if ((sd4 + sd5)/2 - distFromTarget - targetPos[1]) > 0 and parking:
                        reversing = True
                        motor = -1
                        steering = True
                        turnAngle = maxAngle
                        colourScan = False

