"""Minimal Python + Pygame robotics simulator.

Displays a robot, a target, and obstacles.
Move the robot with arrow keys.
"""

import pygame  # rendering

WIDTH, HEIGHT = 800, 600
FPS = 60
ROBOT_SIZE = 30
ROBOT_SPEED = 300  # pixels per second
TARGET_RADIUS = 15

ROBOT_START = [100, 100]
TARGET_POS = (700, 500)
OBSTACLES = [
    pygame.Rect(250, 150, 120, 40),
    pygame.Rect(450, 300, 40, 200),
    pygame.Rect(150, 400, 200, 40),
]

COLOR_BG = (30, 30, 30)
COLOR_ROBOT = (80, 150, 255)
COLOR_TARGET = (80, 220, 120)
COLOR_OBSTACLE = (130, 130, 130)
COLOR_TEXT = (255, 255, 255)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Minimal Robotics Simulator")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    robot = pygame.Rect(ROBOT_START[0], ROBOT_START[1], ROBOT_SIZE, ROBOT_SIZE)
    reached = False
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * ROBOT_SPEED * dt
        dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * ROBOT_SPEED * dt
        robot.x += int(round(dx))
        robot.y += int(round(dy))
        robot.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        target_rect = pygame.Rect(
            TARGET_POS[0] - TARGET_RADIUS,
            TARGET_POS[1] - TARGET_RADIUS,
            TARGET_RADIUS * 2,
            TARGET_RADIUS * 2,
        )
        reached = robot.colliderect(target_rect)

        screen.fill(COLOR_BG)
        for obs in OBSTACLES:
            pygame.draw.rect(screen, COLOR_OBSTACLE, obs)
        pygame.draw.circle(screen, COLOR_TARGET, TARGET_POS, TARGET_RADIUS)
        pygame.draw.rect(screen, COLOR_ROBOT, robot)

        hint = "Reached target!" if reached else "Arrow keys to move | ESC to quit"
        screen.blit(font.render(hint, True, COLOR_TEXT), (10, 10))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
