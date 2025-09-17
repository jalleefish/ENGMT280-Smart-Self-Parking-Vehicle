import pygame, random, math, cv2, numpy as np

#  Course layout 
WIDTH, HEIGHT = 1690, 495
BAY_START = 345
BAY_COUNT = 8
LANE_TOP = 0
LANE_BOT = 265
BAY_W, BAY_H = 125, 230
TILE_WIDTH, TILE_HEIGHT = 64, 8

#  Car Parameters 
car_l, car_w = 158, 85
car_x, car_y = 60, LANE_BOT/2 - car_w/2
car_speed = 2.0
TURN_RAD = 211.36
MAX_ANGLE = math.radians(30.8) # Turn radius 211.36 at max steering angle 30.8 degrees
car_theta = 0.0          # car orientation in radians (0 = pointing right)
reverse_speed = -2.0       # reverse speed

#  Colours 
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GRAY   = (120, 120, 120)
RED    = (200, 0, 0)
GREEN  = (0, 180, 0)
BLUE   = (60, 80, 255)
YELLOW = (250, 225, 0)
PALETTE = [RED, GREEN, BLUE, YELLOW]

#  Parking spots 
spots = list(range(BAY_COUNT))
available_spots = random.sample(spots, random.randint(2, 6))
occupied_spots = [s for s in spots if s not in available_spots]
available_colours = [random.choice(PALETTE) for _ in available_spots]

#  State 
state = "find_ref"
target_colour = random.choice(available_colours)
sensor_poll_counter = 0
SENSOR_POLL_RATE = 10  # check every 10 frames (~6 times per second at 60 FPS)
PARK_TOL = 5  # pixels
target_x, target_y = 0, 0  # to be set when seeking spot
spot_index = 0  # to be set when seeking spot
printed_find_ref = False  # flag to ensure "Finding reference colour" is printed only once
new_target = None  # to store the detected reference colour

#  Pygame setup 
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SSV Simulation")
clock = pygame.time.Clock()
 
def build_obstacles():
    obs = []
    # Walls
    obs.append(pygame.Rect(0, LANE_BOT, BAY_START, HEIGHT))
    obs.append(pygame.Rect(WIDTH - BAY_START, LANE_BOT, BAY_START, HEIGHT))
    # Parked cars
    for i in spots:
        if i not in available_spots:
            x = BAY_START + i * BAY_W + BAY_W / 2 - car_w / 2
            y = LANE_BOT + 30
            obs.append(pygame.Rect(x, y, car_w, car_l))
    return obs
obstacles = build_obstacles()

font = pygame.font.SysFont("Arial", 16)
 
def draw_course():
    screen.fill(WHITE)
    # Walls
    pygame.draw.rect(screen, BLACK, (0, LANE_BOT, BAY_START, HEIGHT))
    pygame.draw.rect(screen, BLACK, (WIDTH - BAY_START, LANE_BOT, BAY_START, HEIGHT))
    # Lane/border lines
    pygame.draw.line(screen, BLACK, (0, HEIGHT - 5), (WIDTH, HEIGHT - 5), TILE_HEIGHT)
    pygame.draw.line(screen, BLACK, (0, 0), (WIDTH, 0), TILE_HEIGHT)
    pygame.draw.line(screen, BLACK, (0, 0), (0, HEIGHT), TILE_HEIGHT)
    pygame.draw.line(screen, BLACK, (WIDTH, 0), (WIDTH, HEIGHT), TILE_HEIGHT)
    
def draw_tiles():
    # Target tiles (reference markers at ends)
    pygame.draw.rect(screen, target_colour, (225, LANE_BOT-1, TILE_WIDTH, TILE_HEIGHT))
    pygame.draw.rect(screen, target_colour, (WIDTH - 225 - TILE_WIDTH, LANE_BOT-1, TILE_WIDTH, TILE_HEIGHT))
    # Parking spots
    for i in spots:
        x = BAY_START + i * BAY_W
        rect = pygame.Rect(x, LANE_BOT, BAY_W, BAY_H)
        pygame.draw.rect(screen, GRAY, rect, 2)
        if i in available_spots:
            colour = available_colours[available_spots.index(i)]
            pygame.draw.rect(screen, colour, (x + BAY_W / 2 - TILE_WIDTH / 2, HEIGHT - TILE_HEIGHT-1, TILE_WIDTH, TILE_HEIGHT))
        else:
            pygame.draw.rect(screen, BLACK, (x + BAY_W/2 - car_w/2, LANE_BOT+30, car_w, car_l))
    
def draw_car():
    # Draw rotated car centered at (car_cx, car_cy)
    global camera, car_cx, car_cy
    car_cx, car_cy = (car_x + car_l/2), (car_y + car_w/2)

    # Create a rotated car surface
    car_surface = pygame.Surface((car_l, car_w), pygame.SRCALPHA)
    pygame.draw.rect(car_surface, BLUE, (0, 0, car_l, car_w))
    # Wheels (optional detail)
    pygame.draw.rect(car_surface, BLACK, (15, 0, 30, 15))               # front left
    pygame.draw.rect(car_surface, BLACK, (car_l-45, 0, 30, 15))         # front right
    pygame.draw.rect(car_surface, BLACK, (15, car_w-15, 30, 15))        # rear left
    pygame.draw.rect(car_surface, BLACK, (car_l-45, car_w-15, 30, 15)) # rear right

    rotated = pygame.transform.rotate(car_surface, -math.degrees(car_theta))
    rect = rotated.get_rect(center=(car_cx, car_cy))
    screen.blit(rotated, rect.topleft)

    # Camera apex: compute in car local coords and rotate into world
    # choose local offset relative to car center: (local_x, local_y)
    # local_x positive = forward (right side of car image), local_y positive = down
    # for a "front middle" camera choose e.g. local = (car_l/2 - 10, 0)
    local_cam_x = 0
    local_cam_y = car_w/2
    # Rotate local -> world
    wx = local_cam_x * math.cos(car_theta) - local_cam_y * math.sin(car_theta)
    wy = local_cam_x * math.sin(car_theta) + local_cam_y * math.cos(car_theta)
    camera = (car_cx + wx, car_cy + wy)

    # draw small red dot at camera (for debug)
    pygame.draw.circle(screen, (255, 0, 0), (int(camera[0]), int(camera[1])), 5)
    pygame.draw.circle(screen, (255, 0, 0), (int(car_cx), int(car_cy)), 5)

  
def close_to_palette(colour, palette, tol=10):
    for p in palette:
        if all(abs(int(c) - int(pc)) <= tol for c, pc in zip(colour, p)):
            return p
    return None

def scan_and_draw_cone(*, apex, cone_width, cone_length, num_rays, obstacles, frame_rgb, screen, car_theta):
    last_colour = None
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    x0, y0 = map(int, apex)
    half_width = cone_width / 2

    for i in range(num_rays):
        t = i / (num_rays - 1)
        local_x = cone_length       # forward
        local_y = -half_width + t * cone_width  # lateral offset

        # rotate into world coordinates
        world_dx = local_x * math.cos(car_theta+math.pi/2) - local_y * math.sin(car_theta+math.pi/2)
        world_dy = local_x * math.sin(car_theta+math.pi/2) + local_y * math.cos(car_theta+math.pi/2)

        end_x, end_y = x0 + world_dx, y0 + world_dy

        # Ray stepping (collision detection)
        dx, dy = end_x - x0, end_y - y0
        steps = max(abs(int(dx)), abs(int(dy)))
        if steps == 0:
            continue

        for s in range(steps):
            px = int(x0 + dx * s / steps)
            py = int(y0 + dy * s / steps)

            if not (0 <= px < WIDTH and 0 <= py < HEIGHT):
                end_x, end_y = px, py
                break
            if any(obs.collidepoint(px, py) for obs in obstacles):
                end_x, end_y = px, py
                break

            colour = tuple(frame_rgb[px, py])
            hit = close_to_palette(colour, PALETTE, tol=40)
            if hit:
                last_colour = hit
                end_x, end_y = px, py
                break

        pygame.draw.aaline(overlay, (0, 255, 0, 80), (x0, y0), (end_x, end_y))

    screen.blit(overlay, (0, 0))
    return last_colour


def cast_sensor_ray(start_pos, direction, max_length, obstacles, surface):
    x0, y0 = start_pos
    dx, dy = direction
    steps = int(max_length)
    distance = max_length

    for s in range(steps):
        px = int(x0 + dx * s)
        py = int(y0 + dy * s)
        if not (0 <= px < WIDTH and 0 <= py < HEIGHT):
            distance = s
            break
        if any(obs.collidepoint(px, py) for obs in obstacles):
            distance = s
            break
    # Draw the ray
    end_x = int(x0 + dx * distance)
    end_y = int(y0 + dy * distance)
    pygame.draw.line(surface, (255, 165, 0), (x0, y0), (end_x, end_y), 2)  # orange color
    return distance

#  Main loop 
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_course()
    draw_tiles()
    draw_car()

    frame_rgb = pygame.surfarray.array3d(screen)
    
    last_colour = scan_and_draw_cone(
        apex=camera,
        cone_width=200,
        cone_length=400,
        num_rays=15,
        obstacles=obstacles,
        frame_rgb=frame_rgb,
        screen=screen,
        car_theta=car_theta  # pass car heading
    )
    
        # === RANGE SENSORS ===
    # sensor offsets relative to car center (local coordinates)
    sensor_offsets = {
        "Side Left":  (car_l/2 - 55, -car_w/2 + 3),
        "Side Right": (car_l/2 - 55,  car_w/2 - 3),
        "Front Mid":  (car_l/2 - 3,    0),
        "Rear Left":  (-car_l/2 + 3,  -car_w/2 + 8),
        "Rear Right": (-car_l/2 + 3,   car_w/2 - 8)
    }

    # compute world positions for sensors (rotate offsets)
    sensor_positions = {}
    for name, (lx, ly) in sensor_offsets.items():
        wx = lx * math.cos(car_theta) - ly * math.sin(car_theta)
        wy = lx * math.sin(car_theta) + ly * math.cos(car_theta)
        sensor_positions[name] = (car_cx + wx, car_cy + wy)

    # base local directions (forward is +x in car local frame)
    base_directions = {
        "Side Left":  (0, -1),
        "Side Right": (0, 1),
        "Front Mid":  (1, 0),
        "Rear Left":  (-1, 0),
        "Rear Right": (-1, 0)
    }

    # rotate directions into world frame
    directions = {}
    for name, (dx, dy) in base_directions.items():
        world_dx = dx * math.cos(car_theta) - dy * math.sin(car_theta)
        world_dy = dx * math.sin(car_theta) + dy * math.cos(car_theta)
        directions[name] = (world_dx, world_dy)

    font = pygame.font.SysFont("Arial", 18)
    sensor_text_y = HEIGHT - 120  # start 120 px from bottom
    sensor_text_x = 10  # left margin

    # store sensor distances
    sensor_distances = {}

    for name, pos in sensor_positions.items():
        dist = cast_sensor_ray(pos, directions[name], WIDTH, obstacles, screen)
        sensor_distances[name] = dist

        # Draw each distance in bottom-left corner
        text = font.render(f"{name}: {dist}mm", True, WHITE)
        screen.blit(text, (sensor_text_x, sensor_text_y))
        sensor_text_y += 20  # next line
        
    text = font.render(f"Angle: {math.degrees(car_theta)}", True, WHITE)
    screen.blit(text, (sensor_text_x, HEIGHT - 140))
    text = font.render(f"Car X: {car_cx}mm", True, WHITE)
    screen.blit(text, (sensor_text_x, HEIGHT - 160))
    text = font.render(f"Car Y: {car_cy}mm", True, WHITE)
    screen.blit(text, (sensor_text_x, HEIGHT - 180))

    if state == "find_ref":
        if not printed_find_ref:
            print("Finding reference colour")
            printed_find_ref = True   # ensure it's only printed once

        car_x += car_speed
        if last_colour in PALETTE and sensor_distances["Side Right"] < car_cy:
            new_target = last_colour
            print(f"Reference colour detected: {last_colour}")
            state = "seek_spot"
            print(f"Seeking spot for colour {new_target}")

    elif state == "seek_spot":
        car_x += car_speed
        if target_colour == last_colour and sensor_distances["Side Right"] > car_cy:
            print("Detected colours:", last_colour)
            # Only count it if the target colour is actually in available spots (not just reference tiles)
            if target_colour in available_colours:
                spot_index = available_spots[available_colours.index(target_colour)]
                target_x = BAY_START + spot_index * BAY_W + BAY_W / 2
                target_y = HEIGHT - TILE_HEIGHT / 2
                state = "Positioning"
                print(f"Positioning for spot {spot_index} at x={target_x}")

    elif state == "Positioning":
        # Use front/rear sensors to prevent overshoot
        front_dist = sensor_distances["Front Mid"]
        rear_dist = (sensor_distances["Rear Left"] + sensor_distances["Rear Right"]) / 2
        left_dist = sensor_distances["Side Left"]
        right_dist = sensor_distances["Side Right"]

        dx = target_x - rear_dist - car_l/2 + TURN_RAD 

        # Move in X direction (forward/backward)
        if abs(dx) > PARK_TOL:
            if dx > 0 and front_dist > PARK_TOL:  # move forward only if front sensor allows
                car_x += min(car_speed, dx, front_dist - PARK_TOL)
            elif dx < 0 and rear_dist > PARK_TOL:  # move backward only if rear sensor allows
                car_x -= min(car_speed, -dx, rear_dist - PARK_TOL)
        
        # Stop completely if within tolerance or blocked by sensors
        if abs(dx) <= PARK_TOL or front_dist <= PARK_TOL or rear_dist <= PARK_TOL:
            state = "Park"
            print(f"Parking in spot {spot_index}")

    elif state == "Park":
        car_speed = -2      # reverse speed
        if car_theta > math.radians(-90):
            # Update position and orientation
            car_x += car_speed * math.cos(car_theta)
            car_y += car_speed * math.sin(car_theta)
            car_theta += (car_speed)/TURN_RAD*1.75*math.tan(MAX_ANGLE)  # changes heading

        # Stop when rear-center close enough to target
        elif car_theta <= math.radians(-90):
            car_theta = math.radians(-90)
            car_y -= car_speed
            if (car_y+car_l) > target_y:
                state = "Parked"
                print(f"Parked in spot {spot_index}")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
