import cv2, time, socket, numpy as np, threading, requests

HOST = "0.0.0.0"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print("Waiting for ESP32...")
conn, addr = server_socket.accept()
print(f"Connected by {addr}")

buffer = ""

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

class Clock:
    def __init__(self, interval: float):
        self.interval: float = interval
        self.last_time = time.time()
        self.running = True

    def start(self):
        self.running = True
        self.last_time = time.time()

    def stop(self):
        self.running = False

    def reset(self):
        self.last_time = time.time()

    def ready(self):
        if not self.running:
            return False
        now = time.time()
        if now - self.last_time >= self.interval:
            self.last_time = now
            return True
        return False
    
clock = Clock(interval=2)  # take snapshot every 2s

latest_frame = None
frame_lock = threading.Lock()
url = "http://192.168.137.136/capture"

def fetch_frames():
    global latest_frame
    while True:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                img_array = np.frombuffer(response.content, np.uint8)
                bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if bgr is not None:
                    with frame_lock:
                        latest_frame = bgr
            else:
                print("HTTP error:", response.status_code)
        except Exception as e:
            print("Error fetching image:", e)

threading.Thread(target=fetch_frames, daemon=True).start()  # start after url is defined       

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
    if clock.ready():
        if sender == 'colourScan':
            colourScan = True
        if sender == 'noScan':
            colourScan == False
        if colourTarget.count(1) >= 2:
            colourScan = False
            break
        if colourScan:
            with frame_lock:
                bgr = latest_frame  # get the most recent frame
            if bgr is not None:
                hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

                # Create ranges for each color
                blue = cv2.inRange(hsv, lowerBlue, upperBlue)
                green = cv2.inRange(hsv, lowerGreen, upperGreen)
                yellow = cv2.inRange(hsv, lowerYellow, upperYellow)
                red1 = cv2.inRange(hsv, lowerRed, upperRed)
                red2 = cv2.inRange(hsv, lowerRed2, upperRed2)
                red = red1 + red2  # Combine the two red masks

                # # Create masks for each color
                # blueMask = cv2.bitwise_and(bgr, bgr, mask=blue)
                # greenMask = cv2.bitwise_and(bgr, bgr, mask=green)
                # yellowMask = cv2.bitwise_and(bgr, bgr, mask=yellow)
                # redMask = cv2.bitwise_and(bgr, bgr, mask=red)
                
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
                            
                cv2.imshow('Original', bgr)
                
                while not(colours == []):
                    coloursX = [sublist[1] for sublist in colours]
                    firstColour = max(coloursX)
                    firstColourIndex = coloursX.index(firstColour)
                    orderedColours.append(colours.pop(firstColourIndex))
                    print(orderedColours[-1])
                if len(orderedColours) > 2:
                    for i in range(2, len(orderedColours)):
                        if (i - 2) not in targetNumbers:
                            if orderedColours[i][0] == orderedColours[0][0] or orderedColours[i][0] == orderedColours[1][0]:
                                if len(targetNumbers) < 2:
                                    targetNumbers.append(i - 2)
                                    
            if len(targetNumbers) >= 1:
                firstTarget = targetNumbers[0]
                msg = f"setFirstTarget:{firstTarget}\n"
                conn.sendall(msg.encode())

            if len(targetNumbers) == 2:
                secondTarget = targetNumbers[1]
                msg = f"setSecondTarget:{secondTarget}\n"
                conn.sendall(msg.encode())    
        else:
            print("Failed to decode image")

    # Keep UI responsive, check for quit every loop iteration
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('+'):
        clock.interval = max(0.5, clock.interval - 0.5)  # faster snapshots
    elif key == ord('-'):
        clock.interval += 0.5  # slower snapshots

cv2.destroyAllWindows()