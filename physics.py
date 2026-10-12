"""Movement and collision detection."""

import pygame
from environments import WORLD_WIDTH, WORLD_HEIGHT, AGENT_SIZE, AGENT_SPEED, GOAL_RADIUS

def execute_action(agent_state, action, environment, dt):
    """
    Execute the action (movement) with collision detection and avoidance.
    Updates agent_state in place.
    """
    # If already crashed, don't move
    if agent_state.is_crashed:
        return

    dx, dy = action
    obstacles = environment["obstacles"]

    # Include dynamic obstacles if present
    if "dynamic_obstacles" in environment:
        dynamic_rects = [dyn_obs.rect for dyn_obs in environment["dynamic_obstacles"]]
        obstacles = obstacles + dynamic_rects

    # Calculate new position
    new_x = agent_state.position.x + int(round(dx))
    new_y = agent_state.position.y + int(round(dy))

    # Test X and Y movement separately for sliding
    test_rect_x = pygame.Rect(new_x, agent_state.position.y, AGENT_SIZE, AGENT_SIZE)
    test_rect_y = pygame.Rect(agent_state.position.x, new_y, AGENT_SIZE, AGENT_SIZE)

    x_blocked = any(test_rect_x.colliderect(obs) for obs in obstacles)
    y_blocked = any(test_rect_y.colliderect(obs) for obs in obstacles)

    # Apply movement if not blocked
    if not x_blocked:
        agent_state.position.x = new_x
    if not y_blocked:
        agent_state.position.y = new_y

    # Obstacle avoidance: try perpendicular directions when blocked
    if x_blocked or y_blocked:
        if x_blocked:
            for direction in [1, -1]:
                alt_dy = direction * AGENT_SPEED * dt
                alt_test_y = pygame.Rect(
                    agent_state.position.x,
                    agent_state.position.y + int(round(alt_dy)),
                    AGENT_SIZE, AGENT_SIZE
                )
                if not any(alt_test_y.colliderect(obs) for obs in obstacles):
                    agent_state.position.y += int(round(alt_dy))
                    break
        if y_blocked:
            for direction in [1, -1]:
                alt_dx = direction * AGENT_SPEED * dt
                alt_test_x = pygame.Rect(
                    agent_state.position.x + int(round(alt_dx)),
                    agent_state.position.y,
                    AGENT_SIZE, AGENT_SIZE
                )
                if not any(alt_test_x.colliderect(obs) for obs in obstacles):
                    agent_state.position.x += int(round(alt_dx))
                    break

    # Clamp to world boundaries
    agent_state.position.clamp_ip(pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))


def check_episode_status(agent_state, environment):
    """
    Check if episode is complete (goal reached or other terminal conditions).
    Returns: dict with status and collision info
    """
    goal = environment["goal"]
    obstacles = environment["obstacles"]

    goal_rect = pygame.Rect(
        goal[0] - GOAL_RADIUS,
        goal[1] - GOAL_RADIUS,
        GOAL_RADIUS * 2,
        GOAL_RADIUS * 2,
    )

    reached = agent_state.position.colliderect(goal_rect)
    collision = any(agent_state.position.colliderect(obs) for obs in obstacles)

    # Check dynamic obstacle collisions for permanent crash state
    if "dynamic_obstacles" in environment and not agent_state.is_crashed:
        dynamic_rects = [dyn_obs.rect for dyn_obs in environment["dynamic_obstacles"]]
        dynamic_collision = any(agent_state.position.colliderect(obs) for obs in dynamic_rects)
        if dynamic_collision:
            agent_state.is_crashed = True  # Permanent crash state
            collision = True  # Also set collision flag
    else:
        dynamic_collision = False

    return {
        "goal_reached": reached,
        "collision": collision,
        "dynamic_collision": dynamic_collision if "dynamic_obstacles" in environment else False,
        "episode_done": reached or agent_state.is_crashed
    }
