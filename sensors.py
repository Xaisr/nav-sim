"""Simulated sensors."""

import math
import pygame
from environments import WORLD_WIDTH, WORLD_HEIGHT


def lidar_scan(position, obstacles, num_rays=8, max_range=150):
    """
    Perform a lidar scan from the robot's position.
    Casts rays in multiple directions and returns distance to nearest obstacle.
    
    Args:
        position: pygame.Rect of agent position
        obstacles: list of pygame.Rect obstacles
        num_rays: number of rays to cast (default 8, at 45° intervals)
        max_range: maximum detection range in pixels (default 150)
    
    Returns:
        list of distances (pixels) for each ray, or max_range if no obstacle detected
    """
    center_x = position.centerx
    center_y = position.centery
    distances = []
    
    angle_step = 360 / num_rays
    
    for i in range(num_rays):
        angle = i * angle_step
        angle_rad = math.radians(angle)
        
        # Ray direction
        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)
        
        # Step along ray until obstacle or max_range
        distance = max_range
        step_size = 5  # 5px resolution
        
        for step in range(0, max_range, step_size):
            test_x = center_x + dx * step
            test_y = center_y + dy * step
            
            # Check bounds
            if test_x < 0 or test_x > WORLD_WIDTH or test_y < 0 or test_y > WORLD_HEIGHT:
                distance = step
                break
            
            # Check obstacle collision
            test_point = pygame.Rect(test_x, test_y, 1, 1)
            for obs in obstacles:
                if test_point.colliderect(obs):
                    distance = step
                    break
            
            if distance < max_range:
                break
        
        distances.append(distance)
    
    return distances
