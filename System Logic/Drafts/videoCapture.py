import cv2, time, socket, numpy as np, threading

HOST = "0.0.0.0"
PORT = 5000
buffer = ""

indexRanging1 = [(175, 225), (225, 275), (275, 325), (325, 375)]
indexRanging2 = [(325, 375), (275, 325), (225, 275), (175, 225)]

colourCheck = 1
colourTarget = [0, 0, 0, 0]
coloursFound = 0
colours = []
colourPos = []
target = True
targetPos = []
run = True
sender = ''
receiver = ''
colourScan = True
targetNumbers = []
firstTarget = -1
secondTarget = -1

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print("Waiting for ESP32...")
conn, addr = server_socket.accept()
print(f"Connected by {addr}")

def comms():
    global sender, buffer
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        buffer += data
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if line:
                sender = line
                print("Sender:", sender)

threading.Thread(target=comms, daemon=True).start()

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

#url = 0
url = "http://192.168.137.136:81/stream"
cap = cv2.VideoCapture(url)  # Open the ESP32-CAM stream

while True:
    rightSensor = distance[0]
    frontSensor = distance[1]
    backAverage = (distance[3] + distance[4]) / 2
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
                
    if len(greenContours) != 0:
        for greenContour in greenContours:
            if cv2.contourArea(greenContour) > 500:
                x, y, w, h = cv2.boundingRect(greenContour)
                cv2.rectangle(bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
                if colour == []:
                    colour = [2, x, y, w, h]
                elif (w * h) > (colour[3] * colour[4]):
                    colour = [2, x, y, w, h]
                
    if len(yellowContours) != 0:
        for yellowContour in yellowContours:
            if cv2.contourArea(yellowContour) > 500:
                x, y, w, h = cv2.boundingRect(yellowContour)
                cv2.rectangle(bgr, (x, y), (x + w, y + h), (0, 255, 255), 2)
                if colour == []:
                    colour = [1, x, y, w, h]
                elif (w * h) > (colour[3] * colour[4]):
                    colour = [1, x, y, w, h]
                
    if len(redContours) != 0:
        for redContour in redContours:
            if cv2.contourArea(redContour) > 500:
                x, y, w, h = cv2.boundingRect(redContour)
                cv2.rectangle(bgr, (x, y), (x + w, y + h), (0, 0, 255), 2)
                if colour == []:
                    colour = [0, x, y, w, h]
                elif (w * h) > (colour[3] * colour[4]):
                    colour = [0, x, y, w, h]

    if rightSensor > 100:
        target = False

    if not(colour == []): 
        if target: # looking for target colours
            colourTarget[colour[0]] = 1
        else:
            if colourTarget[colour[0]] and rightSensor > 100:
                print('target found')
                if frontSensor > backAverage:
                    for i in range(0, len(indexRanging1)):
                        if backAverage in range(indexRanging1[i]):
                            if (i) not in targetNumbers:
                                targetNumbers.append(i)
                else:
                    for i in range(0, len(indexRanging2)):
                        if frontSensor in range(indexRanging1[i]):
                            if (i + 4) not in targetNumbers:
                                targetNumbers.append(i + 4)
                if targetNumbers == []:
                    print('out of ranges')
                else:
                    print(targetNumbers)
                    
    if len(targetNumbers) >= 1:
        firstTarget = targetNumbers[0]
        msg = f"setFirstTarget:{firstTarget}\n"
        conn.sendall(msg.encode())

    if len(targetNumbers) == 2:
        secondTarget = targetNumbers[1]
        msg = f"setSecondTarget:{secondTarget}\n"
        conn.sendall(msg.encode())
        
                


                




    # Display the processed images
    cv2.imshow('Original', bgr)

    # Wait 1ms and check for 'q' key to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(0.1)

cap.release()
cv2.destroyAllWindows()