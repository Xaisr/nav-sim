"""Drawing and UI."""

import math
import pygame
from environments import COLOR_BG, COLOR_AGENT, COLOR_GOAL, COLOR_OBSTACLE, COLOR_TEXT, GOAL_RADIUS


def render(screen, agent_state, environment, episode_status, observations, lidar_data=None):
    """Render the environment, agent, and UI."""
    screen.fill(COLOR_BG)

    # Draw obstacles
    for obs in environment["obstacles"]:
        pygame.draw.rect(screen, COLOR_OBSTACLE, obs)

    # Draw goal
    pygame.draw.circle(screen, COLOR_GOAL, environment["goal"], GOAL_RADIUS)

    # Draw agent
    pygame.draw.rect(screen, COLOR_AGENT, agent_state.position)

    # Draw lidar rays if available
    if lidar_data:
        center_x = agent_state.position.centerx
        center_y = agent_state.position.centery
        num_rays = len(lidar_data)
        angle_step = 360 / num_rays
        
        for i, distance in enumerate(lidar_data):
            angle = i * angle_step
            angle_rad = math.radians(angle)
            end_x = center_x + math.cos(angle_rad) * distance
            end_y = center_y + math.sin(angle_rad) * distance
            
            # Draw ray (green if clear, red if obstacle detected)
            color = (100, 255, 100) if distance >= 150 else (255, 100, 100)
            pygame.draw.line(screen, color, (center_x, center_y), (end_x, end_y), 1)

    # Draw UI hints
    if episode_status["goal_reached"]:
        hint = "Goal reached!"
    elif episode_status["collision"]:
        hint = "Collision!"
    else:
        hint = "Auto-navigating to goal | ESC to quit"

    return hint
