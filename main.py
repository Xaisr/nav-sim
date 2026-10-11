"""Minimal Python + Pygame robotics simulator.

RL-inspired architecture with environment, agent, state, and navigation strategy.

TO ADD A NEW STRATEGY:
1. Define a function that takes (observations, dt) and returns (dx, dy)
2. Add it to NAVIGATION_STRATEGIES dict with a unique key

TO ADD A NEW ENVIRONMENT:
1. Add a new entry to ENVIRONMENTS dict with a unique key
2. Define start position, goal position, and obstacles

CONTROLS:
- 0-9: Switch environments
- Q/W/E/R: Switch navigation strategies
- ESC: Quit
"""

import math
import pygame

# ============== CONFIGURATION ==============
WORLD_WIDTH, WORLD_HEIGHT = 800, 600
FPS = 60
AGENT_SIZE = 30
AGENT_SPEED = 300  # pixels per second
GOAL_RADIUS = 15

# ============== ENVIRONMENTS ==============
# Add new environments by adding new keys (3, 4, 5, etc.)
ENVIRONMENTS = {
    0: {
        "name": "Easy",
        "start": [100, 100],
        "goal": (700, 500),
        "obstacles": [
            pygame.Rect(300, 200, 100, 30),
            pygame.Rect(500, 400, 30, 100),
        ]
    },
    1: {
        "name": "Medium",
        "start": [100, 100],
        "goal": (700, 500),
        "obstacles": [
            pygame.Rect(250, 150, 120, 40),
            pygame.Rect(450, 300, 40, 200),
            pygame.Rect(150, 400, 200, 40),
        ]
    },
    2: {
        "name": "Hard",
        "start": [50, 50],
        "goal": (750, 550),
        "obstacles": [
            pygame.Rect(200, 0, 40, 250),
            pygame.Rect(200, 350, 40, 250),
            pygame.Rect(400, 100, 40, 400),
            pygame.Rect(600, 0, 40, 350),
            pygame.Rect(0, 300, 150, 40),
            pygame.Rect(300, 500, 200, 40),
            pygame.Rect(500, 200, 100, 40),
        ]
    },
    # Add more environments here:
    # 3: {"name": "Expert", "start": [...], "goal": (...), "obstacles": [...]},
}

# ============== COLORS ==============
COLOR_BG = (30, 30, 30)
COLOR_AGENT = (80, 150, 255)
COLOR_GOAL = (80, 220, 120)
COLOR_OBSTACLE = (130, 130, 130)
COLOR_TEXT = (255, 255, 255)


# ============== STATE REPRESENTATION ==============
class AgentState:
    """Represents the agent's current state."""
    def __init__(self, position):
        self.position = position  # pygame.Rect
        self.distance_to_goal = 0.0
        self.is_colliding = False


# ============== OBSERVATIONS ==============
def get_observations(agent_state, environment):
    """Extract observations from the environment for the agent."""
    center = (agent_state.position.centerx, agent_state.position.centery)
    goal = environment["goal"]
    distance = math.hypot(center[0] - goal[0], center[1] - goal[1])
    return {
        "position": center,
        "goal": goal,
        "distance": distance,
        "obstacles": environment["obstacles"]
    }


# ============== NAVIGATION STRATEGIES ==============
def naive_direct_navigation(observations, dt):
    """
    Strategy: Move directly toward goal, slide when blocked.
    Returns: (dx, dy) movement vector
    """
    position = observations["position"]
    goal = observations["goal"]
    distance = observations["distance"]

    if distance == 0:
        return 0, 0

    # Calculate direction to goal
    dx = goal[0] - position[0]
    dy = goal[1] - position[1]

    # Normalize and scale by speed
    dx = (dx / distance) * AGENT_SPEED * dt
    dy = (dy / distance) * AGENT_SPEED * dt

    return dx, dy


# Registry of navigation strategies - add new strategies here
NAVIGATION_STRATEGIES = {
    0: {
        "name": "Naive Direct",
        "function": naive_direct_navigation
    },
    # Add more strategies here:
    # 1: {"name": "Wall Following", "function": wall_following_navigation},
    # 2: {"name": "A* Pathfinding", "function": astar_navigation},
}


# ============== ACTION EXECUTION ==============
def execute_action(agent_state, action, environment, dt):
    """
    Execute the action (movement) with collision detection and avoidance.
    Updates agent_state in place.
    """
    dx, dy = action
    obstacles = environment["obstacles"]

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


# ============== EPISODE STATUS ==============
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

    return {
        "goal_reached": reached,
        "collision": collision,
        "episode_done": reached
    }


# ============== RENDERING ==============
def render(screen, agent_state, environment, episode_status, observations):
    """Render the environment, agent, and UI."""
    screen.fill(COLOR_BG)

    # Draw obstacles
    for obs in environment["obstacles"]:
        pygame.draw.rect(screen, COLOR_OBSTACLE, obs)

    # Draw goal
    pygame.draw.circle(screen, COLOR_GOAL, environment["goal"], GOAL_RADIUS)

    # Draw agent
    pygame.draw.rect(screen, COLOR_AGENT, agent_state.position)

    # Draw UI hints
    if episode_status["goal_reached"]:
        hint = "Goal reached!"
    elif episode_status["collision"]:
        hint = "Collision!"
    else:
        hint = "Auto-navigating to goal | ESC to quit"

    return hint


# ============== MAIN SIMULATION LOOP ==============
def main():
    pygame.init()
    screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT))
    pygame.display.set_caption("Robotics Simulator - RL Architecture")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    # Initialize environment, strategy, and agent
    current_env_idx = 1
    current_strategy_idx = 0
    environment = ENVIRONMENTS[current_env_idx]
    strategy = NAVIGATION_STRATEGIES[current_strategy_idx]
    agent_state = AgentState(
        pygame.Rect(environment["start"][0], environment["start"][1], AGENT_SIZE, AGENT_SIZE)
    )
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Environment switching: 0-9 keys
                elif event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                                   pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                    env_key = event.key - pygame.K_0
                    if env_key in ENVIRONMENTS:
                        current_env_idx = env_key
                        environment = ENVIRONMENTS[current_env_idx]
                        agent_state = AgentState(
                            pygame.Rect(environment["start"][0], environment["start"][1], AGENT_SIZE, AGENT_SIZE)
                        )
                # Strategy switching: Q, W, E, R keys (0, 1, 2, 3)
                elif event.key == pygame.K_q:
                    if 0 in NAVIGATION_STRATEGIES:
                        current_strategy_idx = 0
                        strategy = NAVIGATION_STRATEGIES[current_strategy_idx]
                        agent_state = AgentState(
                            pygame.Rect(environment["start"][0], environment["start"][1], AGENT_SIZE, AGENT_SIZE)
                        )
                elif event.key == pygame.K_w:
                    if 1 in NAVIGATION_STRATEGIES:
                        current_strategy_idx = 1
                        strategy = NAVIGATION_STRATEGIES[current_strategy_idx]
                        agent_state = AgentState(
                            pygame.Rect(environment["start"][0], environment["start"][1], AGENT_SIZE, AGENT_SIZE)
                        )
                elif event.key == pygame.K_e:
                    if 2 in NAVIGATION_STRATEGIES:
                        current_strategy_idx = 2
                        strategy = NAVIGATION_STRATEGIES[current_strategy_idx]
                        agent_state = AgentState(
                            pygame.Rect(environment["start"][0], environment["start"][1], AGENT_SIZE, AGENT_SIZE)
                        )
                elif event.key == pygame.K_r:
                    if 3 in NAVIGATION_STRATEGIES:
                        current_strategy_idx = 3
                        strategy = NAVIGATION_STRATEGIES[current_strategy_idx]
                        agent_state = AgentState(
                            pygame.Rect(environment["start"][0], environment["start"][1], AGENT_SIZE, AGENT_SIZE)
                        )

        # Get observations from environment
        observations = get_observations(agent_state, environment)

        # Check episode status
        episode_status = check_episode_status(agent_state, environment)

        # Update agent state distance
        agent_state.distance_to_goal = observations["distance"]
        agent_state.is_colliding = episode_status["collision"]

        # Navigation strategy: decide action
        if not episode_status["goal_reached"]:
            action = strategy["function"](observations, dt)
        else:
            action = (0, 0)

        # Execute action
        execute_action(agent_state, action, environment, dt)

        # Render
        hint = render(screen, agent_state, environment, episode_status, observations)

        # Draw UI text
        screen.blit(font.render(hint, True, COLOR_TEXT), (10, 10))
        screen.blit(font.render(f"Distance: {int(observations['distance'])}px", True, COLOR_TEXT), (10, 40))
        screen.blit(font.render(f"Environment: {environment['name']} (0-9 to switch)", True, COLOR_TEXT), (10, 70))
        screen.blit(font.render(f"Strategy: {strategy['name']} (Q/W/E/R to switch)", True, COLOR_TEXT), (10, 100))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
