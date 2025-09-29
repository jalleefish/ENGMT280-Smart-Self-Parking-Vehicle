import cv2, time, socket, numpy as np, threading, requests

# Define color ranges for blue, red, and yellow in HSV
lowerBlue = np.array([90, 110, 130])
upperBlue = np.array([135, 255, 255])
lowerGreen = np.array([40, 70, 80])
upperGreen = np.array([80, 255, 255])
lowerYellow = np.array([20, 30, 100])
upperYellow = np.array([35, 255, 255])
lowerRed = np.array([0, 100, 80])
upperRed = np.array([10, 255, 255])
lowerRed2 = np.array([160, 100, 80])
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
bgr: np.ndarray | None = None

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
        
clock = Clock(interval=3)  # take snapshot every 2s

HOST = "0.0.0.0"
PORT = 5000
url = "http://192.168.137.145:81/stream"  # ESP32-CAM MJPEG stream URL

latest_frame = None
frame_lock = threading.Lock()
streaming = True

def fetch_video():
    global latest_frame
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print("Failed to open video stream")
        return

    while streaming:
        ret, frame = cap.read()
        if not ret:
            continue
        with frame_lock:
            latest_frame = frame.copy()
    cap.release()

# start video thread
threading.Thread(target=fetch_video, daemon=True).start()

# Set up PC <-> ESP32 communication
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
                handle_message(line)
                
def handle_message(line: str):
    global colourScan, distances, sender
    if ":" not in line:
        print(f"Invalid message: {line}")
        return
    
    cmd, value_str = line.split(":", 1)
    value_str = value_str.strip()
    value = None
    if value_str.isdigit():
        value = int(value_str)
    
    if cmd == "distances":
        distances = [int(v) for v in value_str.split(",") if v.strip().isdigit()]
        # print("Distances:", distances)
    elif cmd == "colourScan":
        sender = "colourScan"
    elif cmd == "noScan":
        sender = "noScan"
    else:
        print(f"Unknown command: {cmd}")

threading.Thread(target=comms, daemon=True).start()

while True:
    with frame_lock:
        bgr = latest_frame.copy() if latest_frame is not None else None
    
    if bgr is not None:
        h, w, _ = bgr.shape
        bgr = bgr[95:h, 4*w//10:6*w//10]  # crop to central region
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        conn.sendall(b"motorForward:0\n")

        # Create ranges for each color
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
        cv2.imshow('Original', bgr)
        
        coloursAve = []
        while not(colours == []):
            print('found colour')
            for i in range(0, len(colours)):
                ave = colours[i][1] + colours[i][3]/2
                coloursAve.append(ave)

            closest_value = coloursAve[0]
            min_diff = abs(coloursAve[0] - centre)

            for value in coloursAve:
                current_diff = abs(value - centre)
                if current_diff < min_diff:
                    min_diff = current_diff
                    closest_value = value
            ColourIndex = coloursAve.index(closest_value)
            orderedColours.append(colours[ColourIndex])
            del colours[ColourIndex]
            if len(orderedColours) > 1:
                colours = []
            print(orderedColours[-1])
        if len(orderedColours) > 2:
            for i in range(2, len(orderedColours)):
                if (i - 2) not in targetNumbers:
                    if orderedColours[i][0] == orderedColours[0][0] or orderedColours[i][0] == orderedColours[1][0]:
                        if len(targetNumbers) < 2:
                            targetNumbers.append(i - 2)
    print('target numbers', targetNumbers)
                            
    if len(targetNumbers) >= 1:
        firstTarget = targetNumbers[0]
        msg = f"setFirstTarget:{firstTarget}\n"
        conn.sendall(msg.encode())

    if len(targetNumbers) == 2:
        secondTarget = targetNumbers[1]
        msg = f"setSecondTarget:{secondTarget}\n"
        conn.sendall(msg.encode())   

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        streaming = False
        break

cv2.destroyAllWindows()