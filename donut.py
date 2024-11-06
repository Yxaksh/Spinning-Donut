import os
from math import cos, sin
import pygame
import colorsys

# Colors
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
hue = 0

# Display setup
os.environ['SDL_VIDEO_CENTERED'] = '1'
RESOLUTION = WIDTH, HEIGHT = 800, 800
FPS = 60

# Pixel grid settings
PIXEL_W, PIXEL_H = 20, 20
x_pos, y_pos = 0, 0

grid_w = WIDTH // PIXEL_W
grid_h = HEIGHT // PIXEL_H
grid_size = grid_w * grid_h

A, B = 0, 0
THETA_STEP = 10
PHI_STEP = 3

# Characters for rendering
CHARS = ".,-~:;=!*#$@"

# Torus parameters
R1, R2 = 10, 20
K2 = 200
K1 = grid_h * K2 * 3 / (8 * (R1 + R2))

pygame.init()
screen = pygame.display.set_mode(RESOLUTION)
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 20, bold=True)

# Function to convert HSV to RGB color
def hsv_to_rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

# Render character on screen
def render_text(char, x, y):
    text = font.render(str(char), True, hsv_to_rgb(hue, 1, 1))
    text_rect = text.get_rect(center=(x, y))
    screen.blit(text, text_rect)

# Main loop variables
k = 0
paused, running = False, True

while running:
    clock.tick(FPS)
    pygame.display.set_caption(f"FPS: {clock.get_fps():.2f}")
    screen.fill(BLACK)

    # Screen buffer initialization
    output = [' '] * grid_size
    zbuffer = [0] * grid_size

    # Calculating points on torus surface
    for theta in range(0, 628, THETA_STEP):
        for phi in range(0, 628, PHI_STEP):

            cosA, sinA = cos(A), sin(A)
            cosB, sinB = cos(B), sin(B)
            costheta, sintheta = cos(theta), sin(theta)
            cosphi, sinphi = cos(phi), sin(phi)

            # Calculating 3D coordinates
            circle_x = R2 + R1 * costheta
            circle_y = R1 * sintheta
            x = circle_x * (cosB * cosphi + sinA * sinB * sinphi) - circle_y * cosA * sinB
            y = circle_x * (sinB * cosphi - sinA * cosB * sinphi) + circle_y * cosA * cosB
            z = K2 + cosA * circle_x * sinphi + circle_y * sinA
            ooz = 1 / z  # Depth (one over z)

            # Projection to 2D screen
            xp = int(grid_w / 2 + K1 * ooz * x)
            yp = int(grid_h / 2 - K1 * ooz * y)
            pos = xp + grid_w * yp

            # Luminance calculation
            L = cosphi * costheta * sinB - cosA * costheta * sinphi - sinA * sintheta + cosB * (
                cosA * sintheta - costheta * sinA * sinphi)

            # Plotting closer pixels with higher luminance
            if ooz > zbuffer[pos]:
                zbuffer[pos] = ooz
                lum_idx = int(L * 8)
                output[pos] = CHARS[lum_idx if lum_idx > 0 else 0]

    # Rendering the frame
    for i in range(grid_h):
        y_pos += PIXEL_H
        for j in range(grid_w):
            x_pos += PIXEL_W
            render_text(output[k], x_pos, y_pos)
            k += 1
        x_pos = 0
    y_pos = 0
    k = 0

    # Rotation and hue shift
    A += 0.5
    B += 0.1
    hue += 0.005

    if not paused:
        pygame.display.update()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                paused = not paused
