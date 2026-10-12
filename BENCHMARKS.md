# Robotics Simulator - Benchmarks & Statistics

This document tracks performance metrics across different navigation strategies and environments.

## System Configuration

- **World Size:** 800x600 pixels
- **Robot Size:** 10x10 pixels
- **Robot Speed:** 300 pixels/second
- **Goal Radius:** 15 pixels
- **FPS:** 60

## Environments

| ID | Name | Description | Obstacles | Difficulty |
|----|------|-------------|-----------|------------|
| 0 | Easy | Simple obstacles with clear paths | 2 obstacles | Low |
| 1 | Medium | More obstacles, moderate complexity | 3 obstacles | Medium |
| 2 | Hard | Dense walls with narrow gaps | 7 obstacles | High |
| 3 | Deceptive Maze | Dead ends and alternating barriers | Multiple barriers | High |
| 4 | Labyrinth | Complex maze with narrow corridors | 18-34px walls | Very High |

## Navigation Strategies

| ID | Name | Type | Description |
|----|------|------|-------------|
| 0 | Naive Direct | Reactive | Move directly toward goal, slide when blocked |
| 1 | A* Pathfinding | Planning | Grid-based optimal pathfinding |

## Performance Metrics

### Environment 0 (Easy)

| Strategy | Success Rate | Path Length | Waypoints | Time to Goal | Notes |
|----------|--------------|-------------|-----------|--------------|-------|
| Naive Direct | ✅ 100% | ~800px | N/A | ~3s | Simple, works well |
| A* Pathfinding | ✅ 100% | ~800px | ~20 | ~3s | Optimal path |

### Environment 1 (Medium)

| Strategy | Success Rate | Path Length | Waypoints | Time to Goal | Notes |
|----------|--------------|-------------|-----------|--------------|-------|
| Naive Direct | ❌ 0% | N/A | N/A | Stuck | Gets stuck at obstacles |
| A* Pathfinding | ✅ 100% | ~900px | ~100 | ~3s | Solves reliably |

### Environment 2 (Hard)

| Strategy | Success Rate | Path Length | Waypoints | Time to Goal | Notes |
|----------|--------------|-------------|-----------|--------------|-------|
| Naive Direct | ❌ 0% | N/A | N/A | Stuck | Cannot navigate dense walls |
| A* Pathfinding | ✅ 100% | ~1000px | ~120 | ~4s | Handles narrow gaps |

### Environment 3 (Deceptive Maze)

| Strategy | Success Rate | Path Length | Waypoints | Time to Goal | Notes |
|----------|--------------|-------------|-----------|--------------|-------|
| Naive Direct | ❌ 0% | N/A | N/A | Stuck | Trapped by dead ends |
| A* Pathfinding | ✅ 100% | ~1100px | ~123 | ~4s | Navigates maze structure |

### Environment 4 (Labyrinth)

| Strategy | Success Rate | Path Length | Waypoints | Time to Goal | Notes |
|----------|--------------|-------------|-----------|--------------|-------|
| Naive Direct | ❌ 0% | N/A | N/A | Stuck | Fails immediately |
| A* Pathfinding | ✅ 100% | ~1500px | ~328 | ~5s | Requires 10px robot for 18px corridors |

## Key Findings

### Robot Size Impact
- **20px robot:** Cannot navigate Environment 4 (18px corridors)
- **10px robot:** Successfully navigates all environments
- Corridor width must be ≥ robot size for passability

### A* Grid Resolution
- **10px grid:** Best balance for 10px robot
- 31x41 grid for Environment 4
- 79.9% blocked cells in Labyrinth
- Explores all necessary nodes for optimal path

### Strategy Comparison
- **Naive Direct:** Fails on any environment with obstacles requiring detours
- **A* Pathfinding:** Solves all environments optimally
- A* is guaranteed optimal on static, fully-known grids

## Future Benchmarks to Track

### Planned Features
- [ ] Lidar-based navigation (partial observability)
- [ ] D* Lite (dynamic replanning)
- [ ] RRT (sampling-based planning)
- [ ] Potential fields (continuous control)
- [ ] RL agents (learned policies)

### Metrics to Add
- [ ] Sensor range vs success rate
- [ ] Computation time per strategy
- [ ] Memory usage
- [ ] Path smoothness
- [ ] Replanning frequency (for dynamic environments)
- [ ] Robustness to sensor noise

## Changelog

### 2026-10-12
- Added lidar sensor (8 rays, 150px range)
- Robot size reduced to 10px
- A* grid resolution set to 10px
- Environment 4 now solvable with 10px robot
- Created benchmark tracking system
