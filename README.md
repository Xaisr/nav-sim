# Robotics Simulator - RL-Inspired Navigation Testbed

A progressively autonomous navigation environment designed for exploring robotics algorithms, from classical pathfinding to reinforcement learning and space robotics.

## Vision

Build an extensible, modular robotics simulator that evolves from simple manual control into a comprehensive testbed for:

### Classical Planning
- **Algorithms:** A*, D*, D* Lite, RRT, RRT*, Theta*, Hybrid A*, State Lattices
- **Focus:** Optimal pathfinding in known environments

### Partial Observability & SLAM
- **Algorithms:** Frontier Exploration, EKF-SLAM, Particle Filter SLAM, Belief State Planning, POMDP Solvers
- **Focus:** Navigation with incomplete information, map building

### Dynamic Environments
- **Algorithms:** Real-time MPC, Trajectory Optimization, Potential Fields, Lyapunov Stability Analysis
- **Focus:** Adapting to changing conditions, moving obstacles

### Space Robotics
- **Algorithms:** PID, LQR, MPC, iLQR, Clohessy-Wiltshire (orbital mechanics), Trajectory Optimization
- **Focus:** Dynamics, thrust, fuel constraints, orbital mechanics

### Multi-Agent Swarm Coordination
- **Algorithms:** Multi-Agent A* (CBS), Consensus Algorithms, Distributed Optimization, Game Theory (Nash Equilibrium, Stackelberg Games)
- **Focus:** Cooperative/competitive scenarios, system-level coordination

### Dynamic Systems & Game Theory
- **Algorithms:** Minimax, Monte Carlo Tree Search (MCTS), Differential Games, Potential Fields
- **Focus:** Strategic decision-making, competition, prediction

### Reinforcement Learning
- **Algorithms:** Q-Learning, DQN, PPO, SAC, Model-Based RL (Dreamer, TD-MPC)
- **Focus:** Learning from experience, adaptability, sim-to-real transfer

The architecture follows the RL paradigm: **Agent observes state → chooses action → receives reward**.

## Architecture

### Modular Structure

```
robotics/
├── main.py              # Main game loop and orchestration
├── environments.py      # World constants, environment definitions
├── agent.py             # Agent state and observations
├── physics.py           # Movement, collision detection, episode status
├── renderer.py          # Drawing and UI
├── sensors.py           # Lidar sensor implementation
├── strategies.py        # Navigation strategy registry (A*, reactive, etc.)
├── BENCHMARKS.md        # Performance metrics and comparisons
└── ideas.md             # Architecture mapping and roadmap
```

### Key Concepts

- **Environment:** World with obstacles, goal, and start position
- **Agent State:** Position, distance to goal, crash status
- **Observations:** Position, goal, distance, obstacles, lidar data
- **Action:** Movement vector (dx, dy)
- **Episode Status:** Goal reached, collision, episode done
- **Strategy:** Navigation algorithm (Naive, A*, D*, etc.)

## Current Capabilities

### Environments (6)

| ID | Name | Description | Challenge |
|----|------|-------------|-----------|
| 0 | Easy | Simple obstacles with clear paths | Basic navigation |
| 1 | Medium | More obstacles, moderate complexity | Obstacle avoidance |
| 2 | Hard | Dense walls with narrow gaps | Path planning |
| 3 | Deceptive Maze | Dead ends and alternating barriers | Non-greedy routing |
| 4 | Labyrinth | Complex maze with narrow corridors | Stochastic exploration |
| 5 | Dynamic Maze | 5 moving obstacles, crash on collision | Dynamic replanning |

### Navigation Strategies (3)

| ID | Name | Type | Success Rate (Env 4) |
|----|------|------|------------------------|
| 0 | Naive Direct | Reactive | 0% (gets stuck) |
| 1 | A* Pathfinding | Planning | 100% (deterministic) |
| 2 | A* w/ Incremental Discovery | Planning | 50-80% (stochastic) |

### Features

- **Lidar Sensor:** 8 rays, 150px range, ray casting
- **Partial Observability:** Robot discovers obstacles via lidar
- **Dynamic Obstacles:** Moving obstacles with velocity and bounds
- **Crash State:** Permanent crash on dynamic obstacle collision
- **Modular Registries:** Add strategies/environments without replacing code
- **Stochastic Behavior:** Exploration order affects success in complex mazes

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Requirements

- Python 3.13+
- Pygame 2.5.0+

## Run

```powershell
python main.py
```

## Controls

- **0-5:** Switch environments
- **Q:** Naive Direct strategy
- **W:** A* Pathfinding strategy
- **E:** A* with Incremental Discovery (lidar shown)
- **R:** Reserved for future strategies
- **ESC:** Quit

## Key Findings

### Robot Size Impact
- 20px robot: Cannot navigate Environment 4 (18px corridors)
- 10px robot: Successfully navigates all environments
- Corridor width must be ≥ robot size for passability

### Algorithm Comparison
- **Naive Direct:** Fails on any environment requiring detours
- **A* Pathfinding:** Solves all static environments optimally (deterministic)
- **Incremental Discovery:** Solves most environments but stochastic (50-80% on Env 4)
- **Stochasticity:** Partial observability + greedy exploration = non-deterministic results

### Dynamic Environments
- Moving obstacles require proper collision handling
- Crash state prevents "waiting for obstacles to move away"
- Tests ability to predict and avoid moving objects

## Roadmap

### Completed ✅
- Basic Pygame simulator with robot, goal, obstacles
- Collision detection with sliding
- Distance display
- A* pathfinding (grid-based, optimal)
- Lidar sensor implementation
- Partial observability with incremental discovery
- Dynamic obstacles with velocity
- Modular strategy and environment registries
- Benchmarks tracking system

### In Progress 🔄
- Testing dynamic environment (Environment 5)
- Evaluating crash state impact on strategy performance

### Next Steps

#### 1. Add Dynamics (Control Theory + Space Robotics)
- Double-integrator: position + velocity
- Thrust limits, fuel consumption
- Simple MPC or trajectory optimization
- **Algorithms:** PID, LQR, MPC, iLQR, Trajectory Optimization

#### 2. Add RL (AI + Adaptability)
- Gymnasium wrapper
- Reward function
- Train PPO on lidar observations
- **Algorithms:** Q-Learning, DQN, PPO, SAC, Model-Based RL (Dreamer, TD-MPC)

#### 3. Add Swarm (System Structure)
- Multiple agents
- Communication
- Cooperative tasks
- **Algorithms:** Multi-Agent A* (CBS), Consensus Algorithms, Distributed Optimization, Game-Theoretic Approaches (Nash Equilibrium, Stackelberg Games)

#### 4. Deeper Planning
- RRT (sampling-based)
- Potential fields
- Trajectory optimization
- **Algorithms:** RRT, RRT*, RRT-Connect, PRM, Theta*, Hybrid A*, State Lattices

#### 5. Dynamic Systems & Game Theory
- Moving obstacles with predictable/unpredictable patterns
- Multi-agent competitive/cooperative scenarios
- Strategic decision-making under uncertainty
- **Algorithms:** Game Theory (Minimax, Monte Carlo Tree Search), Potential Fields, Lyapunov Stability Analysis, Differential Games

#### 6. Partial Observability & SLAM
- Frontier-based exploration
- Occupancy grid mapping
- Loop closure detection
- **Algorithms:** SLAM (EKF-SLAM, Particle Filter SLAM), Frontier Exploration, Belief State Planning, POMDP Solvers

See `ideas.md` for detailed architecture mapping and algorithm progression.

## Technical Details

### A* Implementation
- Grid size: 10px (matches robot size)
- Heuristic: Manhattan distance
- Replanning: Every 2 seconds in dynamic environments
- Waypoint threshold: 8px

### Lidar Implementation
- 8 rays at 45° intervals
- 150px maximum range
- 5px step resolution
- Returns distance array

### Dynamic Obstacles
- Linear motion with velocity
- Bounce within defined bounds
- Collision causes permanent crash
- Rendered in orange (vs grey for static)

## Contributing

To add a new strategy:
1. Define function in `strategies.py` with signature `(observations, dt)` or `(observations, dt, agent_state, environment)`
2. Add to `NAVIGATION_STRATEGIES` dict
3. Add key mapping in `main.py`

To add a new environment:
1. Add entry to `ENVIRONMENTS` dict in `environments.py`
2. Define start, goal, obstacles
3. Optionally add dynamic obstacles

## License

Educational/research use.

## Acknowledgments

Built with Python and Pygame. Inspired by RL frameworks (Gymnasium) and classical robotics algorithms (A*, D*, RRT).
