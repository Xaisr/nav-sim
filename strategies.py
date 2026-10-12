"""Navigation algorithms and strategy registry."""

import math
import heapq
import pygame
from environments import AGENT_SPEED, WORLD_WIDTH, WORLD_HEIGHT, AGENT_SIZE


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


def world_to_grid(position, obstacles, grid_size=10):
    """
    Convert world coordinates to grid and mark blocked cells.
    Grid size should be >= agent size for valid pathfinding.
    Returns: grid (2D array where True = blocked), grid dimensions
    """
    cols = int(WORLD_WIDTH / grid_size) + 1
    rows = int(WORLD_HEIGHT / grid_size) + 1
    grid = [[False for _ in range(cols)] for _ in range(rows)]

    blocked_count = 0
    # Mark cells that intersect with obstacles as blocked
    for obs in obstacles:
        # Find grid cells this obstacle covers
        start_col = max(0, int(obs.left / grid_size))
        end_col = min(cols - 1, int(obs.right / grid_size))
        start_row = max(0, int(obs.top / grid_size))
        end_row = min(rows - 1, int(obs.bottom / grid_size))

        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                if not grid[row][col]:
                    grid[row][col] = True
                    blocked_count += 1

    return grid, (rows, cols)


def heuristic(a, b):
    """Manhattan distance heuristic for A*."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar_search(grid, start, goal, grid_size=10):
    """
    A* pathfinding algorithm on a grid.
    Returns: list of (x, y) world coordinates representing the path
    """
    rows, cols = len(grid), len(grid[0])

    # Convert world coordinates to grid coordinates
    start_grid = (int(start[1] / grid_size), int(start[0] / grid_size))
    goal_grid = (int(goal[1] / grid_size), int(goal[0] / grid_size))

    # Ensure start and goal are within bounds
    start_grid = (max(0, min(rows - 1, start_grid[0])), max(0, min(cols - 1, start_grid[1])))
    goal_grid = (max(0, min(rows - 1, goal_grid[0])), max(0, min(cols - 1, goal_grid[1])))

    # If start or goal is blocked, try nearby cells
    if grid[start_grid[0]][start_grid[1]]:
        # Find nearest non-blocked cell - expand search radius for dense mazes
        for dr in range(-5, 6):
            for dc in range(-5, 6):
                nr, nc = start_grid[0] + dr, start_grid[1] + dc
                if 0 <= nr < rows and 0 <= nc < cols and not grid[nr][nc]:
                    start_grid = (nr, nc)
                    break
            if not grid[start_grid[0]][start_grid[1]]:
                break

    if grid[goal_grid[0]][goal_grid[1]]:
        for dr in range(-5, 6):
            for dc in range(-5, 6):
                nr, nc = goal_grid[0] + dr, goal_grid[1] + dc
                if 0 <= nr < rows and 0 <= nc < cols and not grid[nr][nc]:
                    goal_grid = (nr, nc)
                    break
            if not grid[goal_grid[0]][goal_grid[1]]:
                break

    # A* algorithm
    open_set = []
    heapq.heappush(open_set, (0, start_grid))
    came_from = {}
    g_score = {start_grid: 0}
    f_score = {start_grid: heuristic(start_grid, goal_grid)}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal_grid:
            # Reconstruct path
            path = []
            while current in came_from:
                # Convert grid coordinates back to world coordinates
                world_x = current[1] * grid_size + grid_size / 2
                world_y = current[0] * grid_size + grid_size / 2
                path.append((world_x, world_y))
                current = came_from[current]
            path.reverse()
            return path

        # Check neighbors (up, down, left, right)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dr, current[1] + dc)

            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols:
                if grid[neighbor[0]][neighbor[1]]:
                    continue  # Blocked cell

                tentative_g = g_score[current] + 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal_grid)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    # No path found
    print(f"[A* SEARCH] No path found - explored {len(came_from)} nodes")
    return None


def astar_navigation(observations, dt, agent_state, environment):
    """
    Strategy: Use A* pathfinding to find optimal path to goal.
    Returns: (dx, dy) movement vector
    """
    position = observations["position"]
    goal = observations["goal"]
    distance = observations["distance"]

    if distance == 0:
        return 0, 0

    # For dynamic environments, invalidate path periodically or on collision
    if "dynamic_obstacles" in environment:
        # Simple approach: replan every 2 seconds in dynamic environments
        if not hasattr(agent_state, 'astar_last_replan'):
            agent_state.astar_last_replan = 0
        if not hasattr(agent_state, 'astar_replan_interval'):
            agent_state.astar_replan_interval = 2.0  # Replan every 2 seconds

        # Check if it's time to replan
        agent_state.astar_last_replan += dt
        if agent_state.astar_last_replan >= agent_state.astar_replan_interval:
            agent_state.astar_path = None  # Force replan
            agent_state.astar_last_replan = 0

    # Initialize path if not already computed
    if not hasattr(agent_state, 'astar_path') or agent_state.astar_path is None:
        # Include dynamic obstacles in grid computation
        all_obstacles = environment["obstacles"].copy()
        if "dynamic_obstacles" in environment:
            all_obstacles += [dyn_obs.rect for dyn_obs in environment["dynamic_obstacles"]]

        grid, (rows, cols) = world_to_grid(position, all_obstacles)
        print(f"[A*] Computing path in {environment['name']}...")
        agent_state.astar_path = astar_search(grid, position, goal)
        agent_state.astar_index = 0

        if agent_state.astar_path:
            print(f"[A*] Path found with {len(agent_state.astar_path)} waypoints")
        else:
            print(f"[A*] NO PATH FOUND in {environment['name']}")

    # Follow the path
    if agent_state.astar_path and agent_state.astar_index < len(agent_state.astar_path):
        target = agent_state.astar_path[agent_state.astar_index]
        dx = target[0] - position[0]
        dy = target[1] - position[1]
        dist_to_target = math.hypot(dx, dy)

        # If close to target waypoint, move to next
        # Threshold should be >= agent size for proper waypoint following
        if dist_to_target < 8:
            agent_state.astar_index += 1
            if agent_state.astar_index < len(agent_state.astar_path):
                target = agent_state.astar_path[agent_state.astar_index]
                dx = target[0] - position[0]
                dy = target[1] - position[1]
                dist_to_target = math.hypot(dx, dy)
            else:
                # Reached final waypoint
                print(f"[A*] Reached final waypoint")
                agent_state.astar_path = None
                return 0, 0

        if dist_to_target > 0:
            dx = (dx / dist_to_target) * AGENT_SPEED * dt
            dy = (dy / dist_to_target) * AGENT_SPEED * dt
            return dx, dy

    return 0, 0


def reactive_lidar_navigation(observations, dt):
    """
    Strategy: Use lidar sensor data for reactive obstacle avoidance.
    Returns: (dx, dy) movement vector
    """
    position = observations["position"]
    goal = observations["goal"]
    distance = observations["distance"]
    lidar = observations.get("lidar", None)

    if distance == 0:
        return 0, 0

    if lidar is None:
        # Fallback to naive direct if no lidar data
        dx = goal[0] - position[0]
        dy = goal[1] - position[1]
        dx = (dx / distance) * AGENT_SPEED * dt
        dy = (dy / distance) * AGENT_SPEED * dt
        return dx, dy

    # Calculate base direction to goal
    dx = goal[0] - position[0]
    dy = goal[1] - position[1]
    dx = (dx / distance) * AGENT_SPEED * dt
    dy = (dy / distance) * AGENT_SPEED * dt

    # Lidar obstacle avoidance
    obstacle_threshold = 50  # pixels
    avoidance_strength = 2.0  # multiplier for avoidance force

    num_rays = len(lidar)
    angle_step = 360 / num_rays

    for i, ray_dist in enumerate(lidar):
        if ray_dist < obstacle_threshold:
            # Obstacle detected in this direction
            angle = i * angle_step
            angle_rad = math.radians(angle)

            # Calculate avoidance force (push away from obstacle)
            # The closer the obstacle, the stronger the avoidance
            avoidance_factor = (obstacle_threshold - ray_dist) / obstacle_threshold
            avoidance_x = -math.cos(angle_rad) * avoidance_strength * avoidance_factor
            avoidance_y = -math.sin(angle_rad) * avoidance_strength * avoidance_factor

            # Add avoidance to movement
            dx += avoidance_x * AGENT_SPEED * dt
            dy += avoidance_y * AGENT_SPEED * dt

    return dx, dy


def dstar_lite_navigation(observations, dt, agent_state, environment):
    """
    Strategy: D* Lite for incremental replanning with partial observability.
    Uses lidar to discover obstacles and updates path incrementally.
    Returns: (dx, dy) movement vector
    """
    position = observations["position"]
    goal = observations["goal"]
    distance = observations["distance"]
    lidar = observations.get("lidar", None)

    if distance == 0:
        return 0, 0

    # Initialize D* Lite state if not exists
    if not hasattr(agent_state, 'dstar_known_obstacles') or agent_state.dstar_known_obstacles is None:
        agent_state.dstar_known_obstacles = []  # List of discovered obstacles
        agent_state.dstar_path = None
        agent_state.dstar_path_index = 0
        agent_state.dstar_grid_size = 10

    # Update known obstacles from lidar
    # For simplicity: if lidar detects obstacle < 150px, add obstacle at that location
    # This is a simplified approach - real implementation would build a proper occupancy grid
    if lidar:
        center_x = position[0]
        center_y = position[1]
        num_rays = len(lidar)
        angle_step = 360 / num_rays

        for i, ray_dist in enumerate(lidar):
            if ray_dist < 150:  # Obstacle detected
                angle = i * angle_step
                angle_rad = math.radians(angle)
                obs_x = center_x + math.cos(angle_rad) * ray_dist
                obs_y = center_y + math.sin(angle_rad) * ray_dist

                # Add obstacle at detected location (10x10 block)
                new_obs = pygame.Rect(obs_x - 5, obs_y - 5, 10, 10)
                # Check if already in known obstacles
                if not any(new_obs.colliderect(existing) for existing in agent_state.dstar_known_obstacles):
                    agent_state.dstar_known_obstacles.append(new_obs)
                    # Mark that path needs replanning
                    agent_state.dstar_path = None

    # Replan if path is None or needs update
    if agent_state.dstar_path is None:
        grid, (rows, cols) = world_to_grid(position, agent_state.dstar_known_obstacles, agent_state.dstar_grid_size)
        print(f"[D* Lite] Replanning with {len(agent_state.dstar_known_obstacles)} known obstacles...")
        agent_state.dstar_path = astar_search(grid, position, goal, agent_state.dstar_grid_size)
        agent_state.dstar_path_index = 0

        if agent_state.dstar_path:
            print(f"[D* Lite] Path found with {len(agent_state.dstar_path)} waypoints")
        else:
            print(f"[D* Lite] No path found with current knowledge")

    # Follow the path
    if agent_state.dstar_path and agent_state.dstar_path_index < len(agent_state.dstar_path):
        target = agent_state.dstar_path[agent_state.dstar_path_index]
        dx = target[0] - position[0]
        dy = target[1] - position[1]
        dist_to_target = math.hypot(dx, dy)

        if dist_to_target < 8:
            agent_state.dstar_path_index += 1
            if agent_state.dstar_path_index < len(agent_state.dstar_path):
                target = agent_state.dstar_path[agent_state.dstar_path_index]
                dx = target[0] - position[0]
                dy = target[1] - position[1]
                dist_to_target = math.hypot(dx, dy)
            else:
                print(f"[D* Lite] Reached final waypoint")
                agent_state.dstar_path = None
                return 0, 0

        if dist_to_target > 0:
            dx = (dx / dist_to_target) * AGENT_SPEED * dt
            dy = (dy / dist_to_target) * AGENT_SPEED * dt
            return dx, dy

    return 0, 0


# Registry of navigation strategies - add new strategies here
NAVIGATION_STRATEGIES = {
    0: {
        "name": "Naive Direct",
        "function": naive_direct_navigation
    },
    1: {
        "name": "A* Pathfinding",
        "function": astar_navigation
    },
    2: {
        "name": "D* Lite",
        "function": dstar_lite_navigation
    },
    # Add more strategies here:
    # 3: {"name": "Wall Following", "function": wall_following_navigation},
}
