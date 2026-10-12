"""Minimal Python + Pygame robotics simulator.

RL-inspired architecture with environment, agent, state, and navigation strategy.

TO ADD A NEW STRATEGY:
1. Define a function that takes (observations, dt) and returns (dx, dy)
2. Add it to NAVIGATION_STRATEGIES dict in strategies.py

TO ADD A NEW ENVIRONMENT:
1. Add a new entry to ENVIRONMENTS dict in environments.py
2. Define start position, goal position, and obstacles

CONTROLS:
- 0-9: Switch environments
- Q: Naive Direct strategy
- W: A* Pathfinding strategy
- E: A* with Incremental Discovery (partial observability, lidar shown)
- R: Reserved for future strategies
- ESC: Quit
"""

import math
import pygame

from environments import (
    WORLD_WIDTH, WORLD_HEIGHT, FPS, AGENT_SIZE,
    ENVIRONMENTS, COLOR_TEXT
)
from agent import AgentState, get_observations, check_stuck_status
from strategies import NAVIGATION_STRATEGIES
from physics import execute_action, check_episode_status
from renderer import render
from sensors import lidar_scan


def reset_agent_state(environment):
    """Create a new agent state and initialize stuck detection."""
    agent_state = AgentState(
        pygame.Rect(environment["start"][0], environment["start"][1], AGENT_SIZE, AGENT_SIZE)
    )
    center = (agent_state.position.centerx, agent_state.position.centery)
    agent_state.best_distance = math.hypot(center[0] - environment["goal"][0], center[1] - environment["goal"][1])
    agent_state.astar_path = None  # Reset A* path
    agent_state.astar_last_replan = 0  # Reset replan timer
    agent_state.dstar_known_obstacles = None  # Reset D* Lite state
    agent_state.is_crashed = False  # Reset crash state
    return agent_state


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
    agent_state = reset_agent_state(environment)
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
                        agent_state = reset_agent_state(environment)
                # Strategy switching: Q, W, E, R keys (0, 1, 2, 3)
                elif event.key == pygame.K_q:
                    if 0 in NAVIGATION_STRATEGIES:
                        current_strategy_idx = 0
                        strategy = NAVIGATION_STRATEGIES[current_strategy_idx]
                        agent_state = reset_agent_state(environment)
                elif event.key == pygame.K_w:
                    if 1 in NAVIGATION_STRATEGIES:
                        current_strategy_idx = 1
                        strategy = NAVIGATION_STRATEGIES[current_strategy_idx]
                        agent_state = reset_agent_state(environment)
                elif event.key == pygame.K_e:
                    if 2 in NAVIGATION_STRATEGIES:
                        current_strategy_idx = 2
                        strategy = NAVIGATION_STRATEGIES[current_strategy_idx]
                        agent_state = reset_agent_state(environment)
                elif event.key == pygame.K_r:
                    if 3 in NAVIGATION_STRATEGIES:
                        current_strategy_idx = 3
                        strategy = NAVIGATION_STRATEGIES[current_strategy_idx]
                        agent_state = reset_agent_state(environment)

        # Update dynamic obstacles if present
        if "dynamic_obstacles" in environment:
            for dyn_obs in environment["dynamic_obstacles"]:
                dyn_obs.update(dt)

        # Perform lidar scan only for strategy E (partial observability)
        lidar_data = None
        if current_strategy_idx == 2:  # D* Lite / partial observability
            lidar_data = lidar_scan(agent_state.position, environment["obstacles"])

        # Get observations from environment
        observations = get_observations(agent_state, environment, lidar_data)

        # Check episode status
        episode_status = check_episode_status(agent_state, environment)

        # Update agent state distance
        agent_state.distance_to_goal = observations["distance"]
        agent_state.is_colliding = episode_status["collision"]

        # Check stuck status (only if not crashed)
        if not agent_state.is_crashed:
            check_stuck_status(agent_state, dt)

        # Navigation strategy: decide action
        if not episode_status["goal_reached"] and not agent_state.is_crashed:
            # Some strategies need agent_state and environment
            if current_strategy_idx == 1:  # A* Pathfinding
                action = strategy["function"](observations, dt, agent_state, environment)
            elif current_strategy_idx == 2:  # D* Lite
                action = strategy["function"](observations, dt, agent_state, environment)
            else:  # Naive Direct, etc.
                action = strategy["function"](observations, dt)
        else:
            action = (0, 0)

        # Execute action (skipped if crashed)
        if not agent_state.is_crashed:
            execute_action(agent_state, action, environment, dt)

        # Render
        hint = render(screen, agent_state, environment, episode_status, observations, lidar_data, current_strategy_idx)

        # Draw UI text
        screen.blit(font.render(hint, True, COLOR_TEXT), (10, 10))
        screen.blit(font.render(f"Distance: {int(observations['distance'])}px", True, COLOR_TEXT), (10, 40))
        screen.blit(font.render(f"Environment: {environment['name']} (0-9 to switch)", True, COLOR_TEXT), (10, 70))
        screen.blit(font.render(f"Strategy: {strategy['name']} (Q/W/E/R to switch)", True, COLOR_TEXT), (10, 100))
        if agent_state.is_stuck:
            screen.blit(font.render("STUCK — no progress", True, (255, 100, 100)), (10, 130))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
