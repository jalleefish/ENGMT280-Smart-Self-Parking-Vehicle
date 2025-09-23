import pygame, random, math, cv2
import numpy as np

pygame.init()
screen = pygame.display.set_mode((1200, 500))
pygame.display.set_caption("SSV Parking Simulation")
clock = pygame.time.Clock()

# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
RED = (200, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 200)
YELLOW = (250, 225, 0)

# Generate Course
spots = list(range(8))  # 8 parking spots
colours = [RED, GREEN, BLUE, YELLOW]
availableSpots = random.sample(spots, random.randint(2,6))
ocupiedSpots = [s for s in spots if s not in availableSpots]

# Assign Random Colours to Spots
availableColours = [random.choice(colours) for _ in availableSpots]
targetColour = random.choice(availableColours)

print(f"Available parking spots: {availableSpots}")
print(f"Parking spot colours: {availableColours}")
print(f"Target parking spot colour: {targetColour}")

# Car & Bay setup
bay_w, bay_h = 60, 120
car_x, car_y = 50, 200
car_w, car_h = 120, 60
speed = 2.5
found_spot = False
parking = False
target_bay = None
angle = 0  # facing right
reverse_phase = 0

def draw_course():
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, (0, 450, 1200, 150))
    pygame.draw.rect(screen, BLACK, (0, 300, 260, 300))
    pygame.draw.rect(screen, BLACK, (920, 300, 280, 300))

def draw_bays():
    for x in ocupiedSpots:
        pygame.draw.rect(screen, GRAY, (x*80+280, 310, bay_w, bay_h))
    for colour, x in zip(availableColours, availableSpots):
        pygame.draw.rect(screen, colour, (x*80+280, 440, bay_w, 10))
    pygame.draw.rect(screen, targetColour, (200, 290, bay_w, 10))

def draw_car(x, y, angle):
    car_surface = pygame.Surface((car_w, car_h), pygame.SRCALPHA)
    pygame.draw.rect(car_surface, GRAY, (0, 0, car_w, car_h))
    pygame.draw.rect(car_surface, BLACK, (0, 0, car_w, car_h), 2)
    pygame.draw.polygon(car_surface, RED, [
        (car_w, car_h//2),
        (car_w-15, 5),
        (car_w-15, car_h-5)
    ])
    rotated = pygame.transform.rotate(car_surface, -angle)
    rect = rotated.get_rect(center=(x, y))
    screen.blit(rotated, rect.topleft)

# Main loop 
running = True
while running:
    draw_course()
    draw_bays()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not found_spot:
        car_x += speed
        if car_x > 280 and not parking:
            bay_index = (car_x - 280) // 80
            if bay_index in availableSpots:
                idx = availableSpots.index(bay_index)
                if availableColours[idx] == targetColour:
                    found_spot = True
                    parking = True
                    target_bay = bay_index
                    print(f"Found target spot at index {target_bay}, starting parking maneuver.")
                    
    else:
        if parking:
            if reverse_phase == 0:  # move forward until aligned with bay
                if car_x < target_bay * 80 + 420 + bay_w // 2:
                    car_x += speed
                else:
                    reverse_phase = 1

            elif reverse_phase == 1:  # reverse + turning into the bay
                if angle > -90:  # adjust this angle for sharper/slower turns
                    angle -= 1
                car_x -= speed * math.cos(math.radians(angle))
                car_y -= speed * math.sin(math.radians(angle))

                # stop once inside bay fully
                if car_y > 370:
                    parking = False

    draw_car(car_x, car_y, angle)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
