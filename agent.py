"""Agent state, observations, and stuck detection."""

import math


class AgentState:
    """Represents the agent's current state."""
    def __init__(self, position):
        self.position = position  # pygame.Rect
        self.distance_to_goal = 0.0
        self.is_colliding = False
        self.is_stuck = False
        self.stuck_timer = 0.0
        self.best_distance = float('inf')


def get_observations(agent_state, environment, lidar_data=None):
    """Extract observations from the environment for the agent."""
    center = (agent_state.position.centerx, agent_state.position.centery)
    goal = environment["goal"]
    distance = math.hypot(center[0] - goal[0], center[1] - goal[1])
    obs = {
        "position": center,
        "goal": goal,
        "distance": distance,
        "obstacles": environment["obstacles"]
    }
    if lidar_data is not None:
        obs["lidar"] = lidar_data
    return obs


def check_stuck_status(agent_state, dt):
    """
    Check if the agent is stuck (not making meaningful progress toward goal).
    Updates agent_state.is_stuck and agent_state.stuck_timer.
    """
    current_distance = agent_state.distance_to_goal

    # Exception: if within 35px of goal, don't consider stuck (already touching goal)
    if current_distance < 35:
        agent_state.is_stuck = False
        return

    # Check if we've made meaningful progress (reduced distance by at least 10 pixels)
    if current_distance < agent_state.best_distance - 10:
        agent_state.best_distance = current_distance
        agent_state.stuck_timer = 0.0
        agent_state.is_stuck = False
    else:
        # No meaningful progress, increment timer
        agent_state.stuck_timer += dt
        if agent_state.stuck_timer >= 3.0:  # 3 seconds threshold
            agent_state.is_stuck = True
