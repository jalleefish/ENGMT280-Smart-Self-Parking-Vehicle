# logic re-write take two

# set up

import pygame as pg
import random
import numpy as np

pi = np.pi
white = (255, 255, 255, 255)
black = (0, 0, 0, 255)
transparent = (0, 0, 0, 0)
red = (255, 0, 0, 255)
yellow = (255, 255, 0, 255)
green = (0, 255, 0, 255)
blue = (0, 0, 255, 255)
purple = (106, 13, 173, 255)
rearcarPos = [50, 100] # rear axle middle
carAngle = 0
throttlePercentage = 0
steeringAngleDeg = 0
maxSteer = 26
wheelRad = 15
run = True
adj = 0
dist = 0

# map creation

pg.init()
scrn = pg.display.set_mode((1400, 500))
disp = pg.Surface((1400, 500), pg.SRCALPHA)
background = pg.Surface((1400, 500))

pg.Surface.fill(background, white)
pg.draw.rect(background, black, (0, 0, 1400, 500), 10)
pg.draw.rect(background, black, (0, 250, 200, 250))
pg.draw.rect(background, black, (800, 270, 600, 230))

colours = [red, yellow, green, blue]
carPositions = [216, 289, 362, 435, 508, 581, 654, 727]
carOrNoCar = [white, white, black, black]

rand = random.sample(range(0, 4), 2)
pg.draw.rect(background, colours[rand[0]], (143, 245, 28.5, 10))
pg.draw.rect(background, colours[rand[1]], (171.5, 245, 28.5, 10))


for i in range (0, 8):
    rand = random.randint(0, 3)
    pg.draw.rect(background, colours[rand], (carPositions[i], 490, 57, 10))
    rand = random.randint(0, 3)
    pg.draw.rect(background, carOrNoCar[rand], (carPositions[i], 300, 57, 170))

# loop states

# 3 sections
firstPark = True
secondPark = False

# states and variables
colourCheck = True
colourTarget = []
coloursFound = False
colourPos = []
parking = False
reversing = False
scan = True
steering = False
leavePark = False
target = 0

go = True

# running loop

while run:

    # car calculations and drawing

    carPos = [rearcarPos[0] + 120*np.cos(carAngle), rearcarPos[1] - 120*np.sin(carAngle)]

    # if near end
    if carPos[0] > 1360:
         throttlePercentage = 0
         go = False

    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                run = False


    dist = throttlePercentage/100
    if adj == 0:
        dAngle = 0
    else: dAngle = dist/adj

    carAngle -= dAngle
    
    rearcarPos = [rearcarPos[0] + dist*np.cos(carAngle), rearcarPos[1] - dist*np.sin(carAngle)]

    carPos = [rearcarPos[0] + 120*np.cos(carAngle), rearcarPos[1] - 120*np.sin(carAngle)]

    wheel1Pos = [carPos[0] + 28.5*np.cos(carAngle + pi/2), carPos[1] - 28.5*np.sin(carAngle + pi/2)]
    wheel2Pos = [carPos[0] + 28.5*np.cos(carAngle - pi/2), carPos[1] - 28.5*np.sin(carAngle - pi/2)]
    wheel3Pos = [rearcarPos[0] + 28.5*np.cos(carAngle + pi/2), rearcarPos[1] - 28.5*np.sin(carAngle + pi/2)]
    wheel4Pos = [rearcarPos[0] + 28.5*np.cos(carAngle - pi/2), rearcarPos[1] - 28.5*np.sin(carAngle - pi/2)]
    steeringAngle = steeringAngleDeg * pi/180
    adj = 120/np.tan(steeringAngle)
    wheel1SteerAngle = np.atan((120)/(adj-80/2))
    wheel2SteerAngle = np.atan((120)/(adj+80/2))
    wheel1Angle = wheel1SteerAngle - carAngle
    wheel2Angle = wheel2SteerAngle - carAngle
    carFront = [carPos[0] + 20*np.cos(carAngle), carPos[1] - 20*np.sin(carAngle)]
    front1Pos = [carFront[0] + 28.5*np.cos(carAngle + pi/2), carFront[1] - 28.5*np.sin(carAngle + pi/2)]
    front2Pos = [carFront[0] + 28.5*np.cos(carAngle - pi/2), carFront[1] - 28.5*np.sin(carAngle - pi/2)]
    carBack = [carPos[0] - 150*np.cos(carAngle), carPos[1] + 150*np.sin(carAngle)]
    back1Pos = [carBack[0] + 28.5*np.cos(carAngle + pi/2), carBack[1] - 28.5*np.sin(carAngle + pi/2)]
    back2Pos = [carBack[0] + 28.5*np.cos(carAngle - pi/2), carBack[1] - 28.5*np.sin(carAngle - pi/2)]

    wheel1Front = [wheel1Pos[0] + wheelRad*np.cos(wheel1Angle), wheel1Pos[1] + wheelRad*np.sin(wheel1Angle)]
    wheel1Back = [wheel1Pos[0] - wheelRad*np.cos(wheel1Angle), wheel1Pos[1] - wheelRad*np.sin(wheel1Angle)]
    wheel2Front = [wheel2Pos[0] + wheelRad*np.cos(wheel2Angle), wheel2Pos[1] + wheelRad*np.sin(wheel2Angle)]
    wheel2Back = [wheel2Pos[0] - wheelRad*np.cos(wheel2Angle), wheel2Pos[1] - wheelRad*np.sin(wheel2Angle)]

    wheel3Front = [wheel3Pos[0] + wheelRad*np.cos(carAngle), wheel3Pos[1] - wheelRad*np.sin(carAngle)]
    wheel3Back = [wheel3Pos[0] - wheelRad*np.cos(carAngle), wheel3Pos[1] + wheelRad*np.sin(carAngle)]
    wheel4Front = [wheel4Pos[0] + wheelRad*np.cos(carAngle), wheel4Pos[1] - wheelRad*np.sin(carAngle)]
    wheel4Back = [wheel4Pos[0] - wheelRad*np.cos(carAngle), wheel4Pos[1] + wheelRad*np.sin(carAngle)]

    pg.Surface.fill(disp, transparent)
    pg.draw.polygon(disp, blue, [front1Pos, front2Pos, back2Pos, back1Pos])
    pg.draw.line(disp, black, wheel1Front, wheel1Back, 6)
    pg.draw.line(disp, black, wheel2Front, wheel2Back, 6)
    pg.draw.line(disp, black, wheel3Front, wheel3Back, 6)
    pg.draw.line(disp, black, wheel4Front, wheel4Back, 6)
    
    pg.Surface.fill(scrn, white)
    scrn.blit(background, (0, 0))
    scrn.blit(disp, (0, 0))
    pg.display.update()

    # scanning loop
    while scan == True:
        for i in range(int(495 - wheel2Pos[1])):
            colour = scrn.get_at(([int(wheel2Pos[0]), int(wheel2Pos[1]+5+i)]))

            #if we see colour
            if colour in colours:
                #print(colour)
                # check if it is a target colour
                if colour in colourTarget:
                    # check if this is a new colour patch by seeing what colour we last saw
                    if colourSeen == False:
                        print("target colour found")
                        colourPos.append(wheel2Pos[0])
                        if firstPark:
                            target = colourPos[0]
                        elif secondPark:
                            target = colourPos[1]
                        else:
                            target = 0
                        colourSeen = True
                # if it is not a target colour    
                else:    
                    colourSeen = True
                    # check if we need a second target colour
                    if not(len(colourTarget) == 2):
                        colourTarget.append(colour)
                scan = False
                break
                        
            if colour == black:
                #print('black')
                colourSeen = False
                scan = False
                break

    # first park:
    if firstPark:
        if not reversing and not steering and not leavePark:
            scan = True
        if not(target == 0):
            parking = True
        
        if steering:
            steeringAngleDeg = 26

            if np.isclose(carAngle, pi/2, atol = 0.005):
                if parking and reversing:
                    steeringAngleDeg = 0
                    steering = False
                    if not leavePark:
                        turnPos = carPos[1]
            
            if np.isclose(carAngle, 0, atol = 0.005):
                if leavePark:
                    steeringAngleDeg = 0
                    steering = False
                    scan = True
                    go = True
                    leavePark = False
                    secondPark = True
                    firstPark = False
                
        else:
            steeringAngle = 0

        if parking:
            if reversing:
                if (carBack[1] + 20) >= 500:
                    throttlePercentage = 0
                    pg.time.wait(2000)
                    print(turnPos)
                    reversing = False
                    parking = False
                    go = True
                    steering = False
                    leavePark = True
                    # remove target
                    target = 0
                else:
                    throttlePercentage = -20
                    go = False
            else:
                if (carPos[0] - 395 - target) > 0 and parking:
                    reversing = True
                    throttlePercentage = -20
                    steering = True
                    scan = False
                    go = False

        if leavePark:
            if (np.isclose(turnPos, carPos[1], atol = 2)):
                steering = True

        if go:
            throttlePercentage = 20



    # second park:
    if secondPark:
        if len(colourPos) > 1:
            target = colourPos[1]

        if not(target == 0):
            parking = True
        
        if not parking:
            scan = True
        
        if steering:
            steeringAngleDeg = 26

            if np.isclose(carAngle, pi/2, atol = 0.005):
                if parking and reversing:
                    steeringAngleDeg = 0
                    steering = False
                    
            if np.isclose(carAngle, 0, atol = 0.005):
                if leavePark:
                    steeringAngleDeg = 0
                    steering = False
                    scan = False
                    go = True
                    leavePark = False
                
        else:
            steeringAngle = 0

        if parking:
            if reversing:
                if (carBack[1] + 20) >= 500:
                    throttlePercentage = 0
                    reversing = False
                    parking = False
                    go = False
                    steering = False
                    # remove target
                    target = 0
                else:
                    throttlePercentage = -20
                    go = False
            else:
                if (carPos[0] - 395 - target) > 0 and parking:
                    reversing = True
                    throttlePercentage = -20
                    steering = True
                    scan = False
                    go = False
        
        if go:
            throttlePercentage = 20



         
