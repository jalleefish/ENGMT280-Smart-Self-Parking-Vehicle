import pygame, random, math
# import imageProcessing as ip

#  Course layout 
WIDTH, HEIGHT = 1690, 495
BAY_START = 345
BAY_COUNT = 8
LANE_TOP = 0
LANE_BOT = 265
BAY_W, BAY_H = 125, 230
TILE_WIDTH, TILE_HEIGHT = 64, 8
START_POS = (60+158/2, LANE_BOT/2 - 85/2, 0.0)  # x,y,theta of centre of car at start

#  Car Parameters 
TURN_RAD = 211.36
MAX_ANGLE = math.radians(30.8) # Turn radius 211.36 at max steering angle 30.8 degrees
SENSOR_POLL_RATE = 10  # check every 10 frames (~6 times per second at 60 FPS)
PARK_TOL = 5  # pixels
CAR_L, CAR_W = 158, 85
front_axle = 7.5  # distance from front of car to front axle
rear_axle = 30   # distance from rear of car to rear axle
car_x, car_y, car_theta = START_POS # car position (From turning centre) and orientation
rear_x, rear_y, car_theta = START_POS   # now START_POS should define rear axle
car_speed = 2.0 #mm/frame
actual_speed = car_speed * 60 # mm/s

L = CAR_L - (front_axle + rear_axle)   # wheelbase
steer_angle = MAX_ANGLE   # fixed steering for demo

rear_x += car_speed * math.cos(car_theta)
rear_y += car_speed * math.sin(car_theta)
car_theta += (car_speed / L) * math.tan(steer_angle)


car_cx = rear_x + (L/2.0) * math.cos(car_theta)
car_cy = rear_y + (L/2.0) * math.sin(car_theta)


#  Colours 
# Create ranges for each color
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PALETTE = [RED, GREEN, BLUE, YELLOW]

#  Parking SPOTS 
SPOTS = list(range(BAY_COUNT))
AVAILABLE_SPOTS = random.sample(SPOTS, random.randint(2, 6))
OCCUPIED_SPOTS = [s for s in SPOTS if s not in AVAILABLE_SPOTS]
AVAILABLE_COLOURS = [random.choice(PALETTE) for _ in AVAILABLE_SPOTS]
TARGET_COLOUR = random.choice(AVAILABLE_COLOURS)

#  State 
state = "find_ref"
sensor_poll_counter = 0
target_x, target_y = 0, 0  # to be set when seeking spot
spot_index = 0  # to be set when seeking spot
printed_find_ref = False  # flag to ensure "Finding reference colour" is printed only once
target_colour = None  # to store the detected reference colour

#  Pygame setup 
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SSV Simulation")
clock = pygame.time.Clock()

def draw_car():
    # Create a rotated car surface
    car_surface = pygame.Surface((CAR_L, CAR_W), pygame.SRCALPHA)
    pygame.draw.rect(car_surface, BLUE, (0, 0, CAR_L, CAR_W))
    # Wheels (local drawing, relative to surface)
    pygame.draw.rect(car_surface, BLACK, (15, 0, 30, 15))               # front left
    pygame.draw.rect(car_surface, BLACK, (CAR_L-45, 0, 30, 15))         # front right
    pygame.draw.rect(car_surface, BLACK, (15, CAR_W-15, 30, 15))        # rear left
    pygame.draw.rect(car_surface, BLACK, (CAR_L-45, CAR_W-15, 30, 15))  # rear right

    rotated = pygame.transform.rotate(car_surface, -math.degrees(car_theta))
    rect = rotated.get_rect(center=(car_cx, car_cy))
    screen.blit(rotated, rect.topleft)
    
    pygame.draw.circle(screen, RED, (int(rear_x), int(rear_y)), 5)


#  Main loop 
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    screen.fill(WHITE)
    draw_car()
    
    car_x += car_speed * math.cos(car_theta)
    car_y += car_speed * math.sin(car_theta)
    car_theta += (car_speed)/TURN_RAD*1.75*math.tan(MAX_ANGLE)  # changes heading
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
