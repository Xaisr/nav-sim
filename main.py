"""Minimal Python + Pygame robotics simulator.

Displays a robot, a target, and obstacles.
Move the robot with arrow keys.
"""

import math
import pygame  # rendering

WIDTH, HEIGHT = 800, 600
FPS = 60
ROBOT_SIZE = 30
ROBOT_SPEED = 300  # pixels per second
TARGET_RADIUS = 15

ENVIRONMENTS = {
    0: {
        "name": "Easy",
        "start": [100, 100],
        "target": (700, 500),
        "obstacles": [
            pygame.Rect(300, 200, 100, 30),
            pygame.Rect(500, 400, 30, 100),
        ]
    },
    1: {
        "name": "Medium",
        "start": [100, 100],
        "target": (700, 500),
        "obstacles": [
            pygame.Rect(250, 150, 120, 40),
            pygame.Rect(450, 300, 40, 200),
            pygame.Rect(150, 400, 200, 40),
        ]
    },
    2: {
        "name": "Hard",
        "start": [50, 50],
        "target": (750, 550),
        "obstacles": [
            pygame.Rect(200, 0, 40, 250),
            pygame.Rect(200, 350, 40, 250),
            pygame.Rect(400, 100, 40, 400),
            pygame.Rect(600, 0, 40, 350),
            pygame.Rect(0, 300, 150, 40),
            pygame.Rect(300, 500, 200, 40),
            pygame.Rect(500, 200, 100, 40),
        ]
    }
}

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

    current_env = 1
    env = ENVIRONMENTS[current_env]
    robot = pygame.Rect(env["start"][0], env["start"][1], ROBOT_SIZE, ROBOT_SIZE)
    reached = False
    collision = False
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_0:
                    current_env = 0
                    env = ENVIRONMENTS[current_env]
                    robot = pygame.Rect(env["start"][0], env["start"][1], ROBOT_SIZE, ROBOT_SIZE)
                    reached = False
                elif event.key == pygame.K_1:
                    current_env = 1
                    env = ENVIRONMENTS[current_env]
                    robot = pygame.Rect(env["start"][0], env["start"][1], ROBOT_SIZE, ROBOT_SIZE)
                    reached = False
                elif event.key == pygame.K_2:
                    current_env = 2
                    env = ENVIRONMENTS[current_env]
                    robot = pygame.Rect(env["start"][0], env["start"][1], ROBOT_SIZE, ROBOT_SIZE)
                    reached = False

        if not reached:
            robot_center = (robot.centerx, robot.centery)
            dx = env["target"][0] - robot_center[0]
            dy = env["target"][1] - robot_center[1]
            distance = math.hypot(dx, dy)
            if distance > 0:
                dx = (dx / distance) * ROBOT_SPEED * dt
                dy = (dy / distance) * ROBOT_SPEED * dt
            else:
                dx = 0
                dy = 0
        else:
            dx = 0
            dy = 0

        new_x = robot.x + int(round(dx))
        new_y = robot.y + int(round(dy))

        test_rect_x = pygame.Rect(new_x, robot.y, ROBOT_SIZE, ROBOT_SIZE)
        test_rect_y = pygame.Rect(robot.x, new_y, ROBOT_SIZE, ROBOT_SIZE)

        x_blocked = any(test_rect_x.colliderect(obs) for obs in env["obstacles"])
        y_blocked = any(test_rect_y.colliderect(obs) for obs in env["obstacles"])

        if not x_blocked:
            robot.x = new_x
        if not y_blocked:
            robot.y = new_y

        if x_blocked or y_blocked:
            if x_blocked:
                for direction in [1, -1]:
                    alt_dy = direction * ROBOT_SPEED * dt
                    alt_test_y = pygame.Rect(robot.x, robot.y + int(round(alt_dy)), ROBOT_SIZE, ROBOT_SIZE)
                    if not any(alt_test_y.colliderect(obs) for obs in env["obstacles"]):
                        robot.y += int(round(alt_dy))
                        break
            if y_blocked:
                for direction in [1, -1]:
                    alt_dx = direction * ROBOT_SPEED * dt
                    alt_test_x = pygame.Rect(robot.x + int(round(alt_dx)), robot.y, ROBOT_SIZE, ROBOT_SIZE)
                    if not any(alt_test_x.colliderect(obs) for obs in env["obstacles"]):
                        robot.x += int(round(alt_dx))
                        break

        robot.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        target_rect = pygame.Rect(
            env["target"][0] - TARGET_RADIUS,
            env["target"][1] - TARGET_RADIUS,
            TARGET_RADIUS * 2,
            TARGET_RADIUS * 2,
        )
        reached = robot.colliderect(target_rect)
        collision = any(robot.colliderect(obs) for obs in env["obstacles"])

        robot_center = (robot.centerx, robot.centery)
        distance = math.hypot(robot_center[0] - env["target"][0], robot_center[1] - env["target"][1])

        screen.fill(COLOR_BG)
        for obs in env["obstacles"]:
            pygame.draw.rect(screen, COLOR_OBSTACLE, obs)
        pygame.draw.circle(screen, COLOR_TARGET, env["target"], TARGET_RADIUS)
        pygame.draw.rect(screen, COLOR_ROBOT, robot)

        if reached:
            hint = "Reached target!"
        elif collision:
            hint = "Collision!"
        else:
            hint = "Auto-navigating to target | ESC to quit"
        screen.blit(font.render(hint, True, COLOR_TEXT), (10, 10))
        screen.blit(font.render(f"Distance: {int(distance)}px", True, COLOR_TEXT), (10, 40))
        screen.blit(font.render(f"Environment: {env['name']} (0/1/2 to switch)", True, COLOR_TEXT), (10, 70))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
