"""Drawing and UI."""

import pygame
from environments import COLOR_BG, COLOR_AGENT, COLOR_GOAL, COLOR_OBSTACLE, COLOR_TEXT, GOAL_RADIUS


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
