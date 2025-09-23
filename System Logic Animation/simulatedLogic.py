import pygame, random, math

pygame.init()
W, H = 1200, 500
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("ENGMT280 - SSV System Logic Simulation")
clock = pygame.time.Clock()

# ---------- Course layout ----------
COURSE_LEN = 220            # nominal centerline of the driving lane
LANE_TOP= 180          # “top” boundary (range sensor sees this)
LANE_BOT = 260          # “bottom” boundary
X0 = 280                # first bay left edge
BAY_GAP = 80
BAY_W, BAY_H = 60, 120
BACK_STRIPE_Y = 440     # y position of coloured back-wall stripe
BAY_ROW_Y = 310         # top of bay rectangles
REF_X, REF_Y = 200, 290 # Reference tile position

# ---------- Car Parameters ----------
car_w, car_h = 120, 60
car_x, car_y = 60, LANE_Y
car_heading_deg = 0          # car faces +x
v_forward = 3.5              # forward speed
v_reverse = 3.0              # reverse speed (straight reverse)
kp_center = 0.04             # simple proportional lane-centering gain

# ---------- Colours ----------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY  = (180, 180, 180)
RED   = (200, 0, 0)
GREEN = (0, 180, 0)
BLUE  = (0, 0, 200)
YELLOW= (250, 225, 0)
PALETTE = [RED, GREEN, BLUE, YELLOW]

# Generate parking map
spots = list(range(8))                                # 8 spots
available_spots = random.sample(spots, random.randint(2, 6))
occupied_spots  = [s for s in spots if s not in available_spots]
available_colours = [random.choice(PALETTE) for _ in available_spots]

# Sensors/camera
CAMERA_SAMPLE_TOL = 18       # x tolerance to consider we’re “in front of” a bay for camera sampling
RAY_AHEAD = 35               # where the arrow tip is

# State machine
state = "seek_ref"           # seek_ref -> drive -> found_target -> align -> reverse_straight -> parked
target_colour = None
target_bay_index = None

# Book-keeping: discovered bay colours as we pass
discovered = {}

# ---------- Drawing ----------
def draw_course():
    screen.fill(WHITE)
    # Road bottom band and walls
    pygame.draw.rect(screen, BLACK, (0, 450, W, 150))         # ground band
    pygame.draw.rect(screen, BLACK, (0, 300, 260, 300))       # left wall block
    pygame.draw.rect(screen, BLACK, (920, 300, 280, 300))     # right wall block
    # Lane bands (just to visualize)
    pygame.draw.line(screen, (60,60,60), (0, LANE_TOP), (W, LANE_TOP), 1)
    pygame.draw.line(screen, (60,60,60), (0, LANE_BOT), (W, LANE_BOT), 1)

def bay_x(i):
    return X0 + i * BAY_GAP

def draw_bays():
    # Occupied bays (solid gray blocks)
    for i in occupied_spots:
        x = bay_x(i)
        pygame.draw.rect(screen, GRAY, (x, BAY_ROW_Y, BAY_W, BAY_H))
    # Available bays (open with coloured back wall stripe only)
    for i, colour in zip(available_spots, available_colours):
        x = bay_x(i)
        # thin back stripe indicates the colour to “read”
        pygame.draw.rect(screen, colour, (x, BACK_STRIPE_Y, BAY_W, 10))

def draw_reference_tile():
    # Color swatch that determines the target (read by camera)
    pygame.draw.rect(screen, BLACK, (REF_X-2, REF_Y-2, BAY_W+4, 14))
    # Pick a ref colour deterministically from our palette to show
    # (we actually draw a random one to the screen; camera will read it)
    pygame.draw.rect(screen, random.choice(PALETTE), (REF_X, REF_Y, BAY_W, 10))

def draw_car(x, y, heading_deg):
    # Body
    car_surface = pygame.Surface((car_w, car_h), pygame.SRCALPHA)
    pygame.draw.rect(car_surface, (210,210,210), (0, 0, car_w, car_h), border_radius=10)
    pygame.draw.rect(car_surface, BLACK, (0, 0, car_w, car_h), 2, border_radius=10)

    # Arrow (forward direction indicator)
    pygame.draw.polygon(car_surface, RED, [
        (car_w-8, car_h//2),
        (car_w-26, 8),
        (car_w-26, car_h-8)
    ])

    rotated = pygame.transform.rotate(car_surface, -heading_deg)
    rect = rotated.get_rect(center=(x, y))
    screen.blit(rotated, rect.topleft)

    # Simple sensor rays (top/bottom range lines)
    cx, cy = x, y
    pygame.draw.line(screen, (255,0,0), (cx, cy), (cx, LANE_TOP), 1)  # top range
    pygame.draw.line(screen, (255,0,0), (cx, cy), (cx, LANE_BOT), 1)  # bottom range

def lane_centering_update(y):
    """Return steering correction (deg) based on range-like distances to lane edges."""
    # Range-like distances
    d_top = y - LANE_TOP
    d_bot = LANE_BOT - y
    # Want equal distances -> center error:
    err = (d_bot - d_top)  # positive -> we are too high; steer down (negative heading)
    return -kp_center * err * 57.3  # scale to “degrees-ish” feel

def camera_read_reference():
    """Sample the screen pixels over the reference tile to set target_colour."""
    sample = screen.get_at((REF_X + BAY_W // 2, REF_Y + 5))  # (r,g,b,a)
    return (sample.r, sample.g, sample.b)

def camera_read_bay(i):
    """Sample the back-wall stripe colour for bay i using screen pixels."""
    x = bay_x(i) + BAY_W // 2
    y = BACK_STRIPE_Y + 5
    px = screen.get_at((x, y))
    return (px.r, px.g, px.b)

def near(a, b, tol):
    return abs(a - b) <= tol

# ---------- Main loop ----------
running = True
align_target_x = None
reverse_target_y = None

while running:
    # Draw static world first
    draw_course()
    draw_bays()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw & read the reference tile every frame until captured
    ref_already = (target_colour is not None)
    if not ref_already:
        draw_reference_tile()

    # --- STATE MACHINE ---
    if state == "seek_ref":
        # Read the reference tile using the virtual camera (pixel sampling)
        target_colour = camera_read_reference()
        # Because PALETTE colours have no alpha and may round slightly, snap to nearest palette colour:
        def nearest_palette(c):
            return min(PALETTE, key=lambda p: (p[0]-c[0])**2 + (p[1]-c[1])**2 + (p[2]-c[2])**2)
        target_colour = nearest_palette(target_colour)
        # After we have the target, start driving forward
        state = "drive"

    elif state == "drive":
        # Lane centering with simple “range sensors”
        steer = lane_centering_update(car_y)
        car_heading_deg = max(min(car_heading_deg + steer, 8), -8)  # clamp tiny heading oscillation
        # Move forward in heading direction
        car_x += v_forward * math.cos(math.radians(car_heading_deg))
        car_y += v_forward * math.sin(math.radians(car_heading_deg))

        # “Camera” checks each bay back-wall stripe as we pass it
        for i in spots:
            bx = bay_x(i) + BAY_W//2
            if near(car_x, bx, CAMERA_SAMPLE_TOL):
                seen = camera_read_bay(i)
                # snap to palette
                seen = min(PALETTE, key=lambda p: (p[0]-seen[0])**2 + (p[1]-seen[1])**2 + (p[2]-seen[2])**2)
                discovered[i] = seen
                if (i in available_spots) and (seen == target_colour):
                    target_bay_index = i
                    state = "found_target"
                    break

    elif state == "found_target":
        # Decide a simple alignment point just beyond the target bay center
        align_target_x = bay_x(target_bay_index) + BAY_W//2 + 40
        state = "align"

    elif state == "align":
        # Drive forward (small lane-centering) until front bumper is past the bay
        steer = lane_centering_update(car_y)
        car_heading_deg = max(min(car_heading_deg + steer, 5), -5)
        car_x += v_forward * math.cos(math.radians(car_heading_deg))
        car_y += v_forward * math.sin(math.radians(car_heading_deg))
        if car_x >= align_target_x:
            # Prepare a straight reverse target Y (center of bay depth)
            reverse_target_y = BAY_ROW_Y + BAY_H - car_h/2 - 6
            # Straighten wheels for a straight reverse
            car_heading_deg = 0
            state = "reverse_straight"

    elif state == "reverse_straight":
        # Reverse straight back into the bay (no turning)
        if car_y < reverse_target_y:
            car_y += v_reverse
        else:
            state = "parked"

    elif state == "parked":
        # Do nothing; show car in final position
        pass

    # Draw the car last (so sensors/arrow are visible above)
    draw_car(car_x, car_y, car_heading_deg)

    # Optional: small HUD text
    font = pygame.font.SysFont(None, 22)
    label = font.render(f"State: {state}  |  Target colour: {target_colour}  |  Target bay: {target_bay_index}", True, (20,20,20))
    screen.blit(label, (20, 12))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
