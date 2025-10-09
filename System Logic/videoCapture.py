import cv2, time, socket, numpy as np, threading, requests

# ---- Logic Configuration ----
start = False
findTarget = True
colourScan = True
streaming = True
calibrating = True
wb_locked = False
recievedFistTarget = False
recievedSecondTarget = False
parkRange = {
             "1" : (350, 390), 
             "2" : (470, 500), 
             "3" : (590, 630), 
             "4" : (700, 730), 
             "5" : (800, 860), 
             "6" : (940, 990), 
             "7" : (1040, 1100),
             "8" : (1170, 1220)
             }
print("Logic Configured")

# ---- Colour Detection Setup ---- 
# Define color ranges for blue, red, and yellow in HSV
lowerBlue = np.array([90, 100, 70])
upperBlue = np.array([135, 255, 255])
lowerGreen = np.array([40, 70, 50])
upperGreen = np.array([80, 255, 255])
lowerYellow = np.array([20, 110, 100])
upperYellow = np.array([35, 255, 255])
lowerRed = np.array([0, 100, 50])
upperRed = np.array([10, 255, 255])
lowerRed2 = np.array([160, 140, 50])
upperRed2 = np.array([180, 255, 255])

minArea = 6000
colourTarget = [-1, -1]
colours = [-1, 0, 0, 0, 0]
targetPos = []
targetNumbers = []
targetColours = []
findPark = False
detectedColour = -1
firstTarget = -1
secondTarget = -1
bgr: np.ndarray | None = None
print("Colours Configured")

# ---- System Timer Setup ----
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
print("Timer Setup")

# ---- ESP32 Main Board Communications Setup ----
HOST = "0.0.0.0"
PORT = 5000
sender = ''
buffer = ""
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print("Waiting for ESP32...")
conn, addr = server_socket.accept()
print(f"ESP32 Connected as {addr}")

def handle_message(line: str):
    global colourScan, distances, sender, recievedFistTarget, recievedSecondTarget
    if ":" not in line:
        print(f"Invalid message: {line}")
        return
    
    cmd, value_str = line.split(":", 1)
    value_str = value_str.strip()
    value = None
    if value_str.isdigit():
        value = int(value_str)
    
    if cmd == "distances":
        raw_values = [int(v) for v in value_str.split(",") if v.strip().isdigit()]
        # pad or trim to ensure exactly 5 values
        while len(raw_values) < 5:
            raw_values.append(0)
        distances = raw_values[:5]
    elif cmd == "colourScan":
        colourScan = True
    elif cmd == "noScan":
        colourScan = False
    elif cmd == "recievedFistTarget":
        recievedFistTarget = True
        print("Confirm recievedFistTarget")
    elif cmd == "recievedSecondTarget":
        recievedSecondTarget = True
        print("Confirm recievedSecondTarget")
    else:
        print(f"Unknown command: {cmd}")

def comms():
    global sender, buffer
    while streaming:
        data = conn.recv(1024).decode()
        if not data:
            break
        buffer += data
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if line:
                handle_message(line)
threading.Thread(target=comms, daemon=True).start()

# ---- Distance Reading ----
distances = [0, 0, 0, 0, 0]  # right, front, left, back right, back left #345
rightSensor = 0
currentPos = 0
def printDistances():
    while streaming:
        print("Current Position: ", currentPos)
        print("Distances: ", distances)
        time.sleep(1)

# ---- ESP32 Camera Communications Setup ----
# cam_ip = "esp32cam.local"
cam_ip = "192.168.137.218"
stream_url = f"http://{cam_ip}:81/stream"  # ESP32-CAM MJPEG stream URL
settings_url = f"http://{cam_ip}/control"
latest_frame = None
frame_lock = threading.Lock()

# ESP32-CAM OV2640 default settings dictionary
esp32cam_defaults = {
    # Automatic controls
    "awb": 1,             # Automatic White Balance ON
    "awb_gain": 1,        # AWB Gain disabled
    "aec": 0,             # Automatic Exposure Control ON
    "aec2": 0,            # Second AE mode ON
    "agc": 1,             # Automatic Gain Control ON
    "gain_ctrl": 1,       # Auto Gain ON
    "ae_level": 200,        # Only used when aec=0

    # Color / image
    "contrast": 1,        # -2 to 2
    "saturation": 2,      # -2 to 2
    "brightness": 1,      # -2 to 2
    "special_effect": 0,  # 0 = None
    "wb_mode": 0,         # 0 = Auto / default

    # # Manual RGB gains (only used if awb=0)
    # "r_gain": 128,        # Red gain
    # "g_gain": 128,        # Green gain
    # "b_gain": 128,        # Blue gain

    # Orientation
    # "vflip": 0,           # Vertical flip OFF
    # "hmirror": 0,         # Horizontal mirror OFF
    # "dcw": 1,             # Downsize image (camera scaling)

    # Resolution / frame
    "framesize": 10,      # FRAMESIZE_UXGA (1600x1200)
    "quality": 10,        # JPEG quality (0 best, 63 worst)
    "fb_count": 1,        # Number of frame buffers
    # "grab_mode": 0,       # CAMERA_GRAB_WHEN_EMPTY
}
for var, val in esp32cam_defaults.items():
    requests.get(f"{settings_url}?var={var}&val={val}")
print("Camera Defaults Set")

def fetch_video():
    global latest_frame, cap
    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        print("Failed to open video stream")
        return

    while streaming:
        ret, frame = cap.read()
        if not ret:
            continue
        with frame_lock:
            latest_frame = frame.copy()
threading.Thread(target=fetch_video, daemon=True).start()

print("Calibration Active")
print("Press 'ENTER' to lock WB, 'G' to start the car and 'Q' to quit at any time")

while streaming:
    with frame_lock:
        bgr = latest_frame.copy() if latest_frame is not None else None
    key = cv2.waitKey(1) & 0xFF
    rightSensor = distances[0]
    frontSensor = distances[1]
    backAverage = (distances[3] + distances[4]) / 2
    
    if backAverage < frontSensor:
        currentPos = backAverage + 105
    else:
        currentPos = 1688 - 80 - frontSensor
    if bgr is not None:
        h, w, _ = bgr.shape
        bgr = bgr[195:h, 2*w//10:5*w//10]  # crop to central region
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        
        colours = [-1, 0, 0, 0, 0]  # reset colours each frame
        detectedColour = -1         # reset detectedColour each frame
        
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
                if cv2.contourArea(blueContour) > minArea:
                    x, y, w, h = cv2.boundingRect(blueContour)
                    cv2.rectangle(bgr, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    colours = [3, x, y, w, h]

                    
        if len(greenContours) != 0:
            for greenContour in greenContours:
                if cv2.contourArea(greenContour) > minArea:
                    x, y, w, h = cv2.boundingRect(greenContour)
                    cv2.rectangle(bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    colours = [2, x, y, w, h]

                    
        if len(yellowContours) != 0:
            for yellowContour in yellowContours:
                if cv2.contourArea(yellowContour) > minArea:
                    x, y, w, h = cv2.boundingRect(yellowContour)
                    cv2.rectangle(bgr, (x, y), (x + w, y + h), (0, 255, 255), 2)
                    colours = [1, x, y, w, h]

                    
        if len(redContours) != 0:
            for redContour in redContours:
                if cv2.contourArea(redContour) > minArea:
                    x, y, w, h = cv2.boundingRect(redContour)
                    cv2.rectangle(bgr, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    colours = [0, x, y, w, h]

        # Display the processed images
        cv2.imshow('Camera Feed', bgr)

    # === Stage 1: Calibration ===
    if calibrating:
        print(currentPos, colours, distances, findTarget, colourScan, colourTarget)
        # print(currentPos, distances)
        if key == 13:  # ENTER
            calibrating = False
            wb_locked = True
            try:
                requests.get(f"{settings_url}?var=awb&val=0")  # disable auto white balance
                print("WB locked. Press 'G' to start the car.")
            except Exception as e:
                print(f"Failed to set WB: {e}")
        elif key == ord('q'):
            streaming = False
            break

    # === Stage 2: WB locked, waiting for Go ===
    elif wb_locked and not start:
        if key == ord('g'):
            threading.Thread(target=printDistances, daemon=True).start()
            start = True
            colours = [-1, 0, 0, 0, 0]
            print("Starting the car...")
            try:
                if conn:
                    conn.sendall(b"motorForward:0\n")
                    print("Sent initial go command to ESP32")
                else:
                    print("No ESP32 connection available")
            except (ConnectionResetError, BrokenPipeError):
                print("Failed to send command: ESP32 disconnected")
        elif key == ord('q'):
            streaming = False
            break
    
    # === Stage 3: Start the car
    elif  start and colourScan:       
        # print(currentPos, colours, distances, findTarget, colourScan, colourTarget, detectedColour)
        if distances[0] < 130 and findTarget:
            detectedColour = colours[0]
            if colours != [-1, 0, 0, 0, 0]:
                if colourTarget == [-1, -1]:
                    colourTarget[0] = detectedColour
                    print("First target colour set to:", colourTarget[0])
                if colourTarget[0] != detectedColour and colourTarget[1] == -1:
                    colourTarget[1] = detectedColour
                    print("Second target colour set to: ", colourTarget[1])
                    findTarget = False
                    findPark = True
                    detectedColour = -1
        
        if distances[0] > 140 and currentPos > 300 and findPark and len(targetNumbers) < 2:
            detectedColour = colours[0]
            if detectedColour in (colourTarget[0], colourTarget[1]):
                for indexKey, (low, high) in parkRange.items():
                    if low <= currentPos <= high:
                        slot = int(indexKey)
                        if slot not in targetNumbers:            # prevent duplicate slots
                            targetNumbers.append(slot)
                            targetColours.append(detectedColour)  # store colour
                            print("Found park at:", targetNumbers, "with colours:", targetColours)

        if recievedFistTarget == False:
            if len(targetNumbers) >= 1:
                firstTarget = targetNumbers[0]
                msg = f"setFirstTarget:{firstTarget}\n"
                conn.sendall(msg.encode())
                print("Sent: ", msg)
        if recievedSecondTarget == False:
            if len(targetNumbers) == 2:
                secondTarget = targetNumbers[1]
                msg = f"setSecondTarget:{secondTarget}\n"
                conn.sendall(msg.encode())
                print("Sent: ", msg)

    if key == ord('q'):
        # Quit safely
        streaming = False
        time.sleep(0.5)  # let threads exit

        try:
            if conn:
                conn.sendall(b"motorStop:0\n")
                conn.close()
                print("ESP32 connection closed")
        except:
            pass

        try:
            server_socket.close()
            print("Server socket closed")
        except:
            pass

        if 'cap' in globals() and cap.isOpened():
            cap.release()

        cv2.destroyAllWindows()
        print("All resources released, program exited.")
        break