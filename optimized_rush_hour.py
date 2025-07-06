from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Set
import heapq
import time
import sys
import tracemalloc
from collections import deque

@dataclass(frozen=True)
class Vehicle:
    vid: int
    row: int
    col: int
    length: int
    horizontal: bool

class Board:
    def __init__(self, vehicles: List[Vehicle], size: int = 6) -> None:
        self.vehicles = vehicles
        self.size = size
        self.nodes_expanded = 0
        # Pre-compute vehicle positions for faster access
        self._vehicle_positions = {v.vid: i for i, v in enumerate(vehicles)}

    def build_occupied(self, state: Tuple[int, ...]) -> Set[Tuple[int, int]]:
        """Build set of occupied cells from current state."""
        occ = set()
        for vid, v in enumerate(self.vehicles):
            r, c = state[vid << 1], state[(vid << 1) + 1]  # Bit shift instead of multiplication
            if v.horizontal:
                occ.update((r, c + k) for k in range(v.length))
            else:
                occ.update((r + k, c) for k in range(v.length))
        return occ

    def move(self, state: Tuple[int, ...], vid: int, delta: int) -> Tuple[int, ...]:
        """Create new state by moving vehicle vid by delta positions."""
        state_list = list(state)
        idx = vid << 1  # Bit shift for vid * 2
        if self.vehicles[vid].horizontal:
            state_list[idx + 1] += delta
        else:
            state_list[idx] += delta
        return tuple(state_list)

    def get_valid_moves(self, state: Tuple[int, ...], vid: int, occ: Set[Tuple[int, int]]) -> List[int]:
        """Get all valid moves for a specific vehicle."""
        moves = []
        v = self.vehicles[vid]
        r, c = state[vid << 1], state[(vid << 1) + 1]
        
        if v.horizontal:
            # Move left
            if c > 0 and (r, c - 1) not in occ:
                moves.append(-1)
            # Move right
            tail = c + v.length - 1
            if tail + 1 < self.size and (r, tail + 1) not in occ:
                moves.append(1)
        else:
            # Move up
            if r > 0 and (r - 1, c) not in occ:
                moves.append(-1)
            # Move down
            tail = r + v.length - 1
            if tail + 1 < self.size and (tail + 1, c) not in occ:
                moves.append(1)
        
        return moves

    def successors(self, state: Tuple[int, ...]) -> List[Tuple[Tuple[int, ...], Tuple[int, int]]]:
        """Generate all possible successor states."""
        succs = []
        occ = self.build_occupied(state)
        
        for vid in range(len(self.vehicles)):
            moves = self.get_valid_moves(state, vid, occ)
            for delta in moves:
                new_state = self.move(state, vid, delta)
                succs.append((new_state, (vid, delta)))
        
        return succs

    def is_goal(self, state: Tuple[int, ...]) -> bool:
        """Check if the red car (vehicle 0) has reached the exit."""
        red_col = state[1]
        red_tail = red_col + self.vehicles[0].length - 1
        return red_tail == self.size - 1

    def manhattan_distance_heuristic(self, state: Tuple[int, ...]) -> int:
        """Simple Manhattan distance heuristic."""
        red_col = state[1]
        red_tail = red_col + self.vehicles[0].length - 1
        return max(0, (self.size - 1) - red_tail)

    def blocking_vehicles_heuristic(self, state: Tuple[int, ...]) -> int:
        """Enhanced heuristic counting blocking vehicles."""
        red_row, red_col = state[0], state[1]
        red_tail = red_col + self.vehicles[0].length - 1
        gap = max(0, (self.size - 1) - red_tail)
        
        if gap == 0:
            return 0
        
        blocks = 0
        # Count vertical vehicles blocking the path
        for vid in range(1, len(self.vehicles)):
            v = self.vehicles[vid]
            if not v.horizontal:  # Only vertical vehicles can block
                c = state[(vid << 1) + 1]
                # Check if this vehicle is in the red car's path
                if red_tail < c <= self.size - 1:
                    r = state[vid << 1]
                    # Check if it overlaps with red car's row
                    if r <= red_row < r + v.length:
                        blocks += 1
        
        return gap + blocks

    def astar(self, start_state: Tuple[int, ...], heuristic: str = 'blocking') -> Optional[Tuple[List[Tuple[int, int]], int]]:
        """A* search implementation with selectable heuristic."""
        h_func = self.blocking_vehicles_heuristic if heuristic == 'blocking' else self.manhattan_distance_heuristic
        
        g_cost = {start_state: 0}
        pq = [(h_func(start_state), 0, start_state)]
        parent = {start_state: None}
        self.nodes_expanded = 0
        
        while pq:
            f, g_cur, current = heapq.heappop(pq)
            
            if g_cur > g_cost.get(current, float('inf')):
                continue
                
            self.nodes_expanded += 1
            
            if self.is_goal(current):
                path = self._reconstruct_path(parent, current)
                total_cost = sum(self.vehicles[vid].length for vid, _ in path)
                return path, total_cost
            
            for next_state, move in self.successors(current):
                vid, _ = move
                move_cost = self.vehicles[vid].length  # Cost = vehicle length
                g_next = g_cur + move_cost
                
                if g_next < g_cost.get(next_state, float('inf')):
                    g_cost[next_state] = g_next
                    parent[next_state] = (current, move)
                    f_next = g_next + h_func(next_state)
                    heapq.heappush(pq, (f_next, g_next, next_state))
        
        return None

    def bfs_solver(self, start_state: Tuple[int, ...]) -> Optional[List[Tuple[int, int]]]:
        """Breadth-First Search implementation."""
        queue = deque([start_state])
        parent = {start_state: None}
        visited = {start_state}
        self.nodes_expanded = 0
        
        while queue:
            current = queue.popleft()
            self.nodes_expanded += 1
            
            if self.is_goal(current):
                return self._reconstruct_path(parent, current)
            
            for next_state, move in self.successors(current):
                if next_state not in visited:
                    visited.add(next_state)
                    parent[next_state] = (current, move)
                    queue.append(next_state)
        
        return None

    def dfs_solver(self, start_state: Tuple[int, ...], max_depth: int = 1000) -> Optional[List[Tuple[int, int]]]:
        """Depth-First Search with depth limiting."""
        stack = [(start_state, 0)]
        parent = {start_state: None}
        visited = {}
        self.nodes_expanded = 0
        
        while stack:
            current, depth = stack.pop()
            
            if current in visited and visited[current] <= depth:
                continue
                
            visited[current] = depth
            self.nodes_expanded += 1
            
            if self.is_goal(current):
                return self._reconstruct_path(parent, current)
            
            if depth < max_depth:
                successors = self.successors(current)
                # Reverse to maintain DFS order
                for next_state, move in reversed(successors):
                    if next_state not in visited or visited[next_state] > depth + 1:
                        parent[next_state] = (current, move)
                        stack.append((next_state, depth + 1))
        
        return None

    def ucs_solver(self, start_state: Tuple[int, ...]) -> Optional[Tuple[List[Tuple[int, int]], int]]:
        """Uniform-Cost Search implementation."""
        g_cost = {start_state: 0}
        pq = [(0, start_state)]
        parent = {start_state: None}
        self.nodes_expanded = 0
        
        while pq:
            cost, current = heapq.heappop(pq)
            
            if cost > g_cost.get(current, float('inf')):
                continue
                
            self.nodes_expanded += 1
            
            if self.is_goal(current):
                path = self._reconstruct_path(parent, current)
                total_cost = sum(self.vehicles[vid].length for vid, _ in path)
                return path, total_cost
            
            for next_state, (vid, delta) in self.successors(current):
                move_cost = self.vehicles[vid].length  # Cost = vehicle length
                g_next = cost + move_cost
                
                if g_next < g_cost.get(next_state, float('inf')):
                    g_cost[next_state] = g_next
                    parent[next_state] = (current, (vid, delta))
                    heapq.heappush(pq, (g_next, next_state))
        
        return None

    def ids_solver(self, start_state: Tuple[int, ...], max_depth: int = 100) -> Optional[List[Tuple[int, int]]]:
        """Iterative Deepening Search implementation."""
        for depth_limit in range(max_depth + 1):
            self.nodes_expanded = 0
            result = self._dfs_limited(start_state, depth_limit)
            if result is not None:
                return result
        return None

    def _dfs_limited(self, start_state: Tuple[int, ...], depth_limit: int) -> Optional[List[Tuple[int, int]]]:
        """Depth-limited search helper for IDS."""
        stack = [(start_state, 0, [])]
        visited = set()
        
        while stack:
            current, depth, path = stack.pop()
            
            if current in visited:
                continue
                
            visited.add(current)
            self.nodes_expanded += 1
            
            if self.is_goal(current):
                return path
            
            if depth < depth_limit:
                for next_state, move in reversed(self.successors(current)):
                    if next_state not in visited:
                        stack.append((next_state, depth + 1, path + [move]))
        
        return None

    @staticmethod
    def _reconstruct_path(parent: Dict, goal_state: Tuple[int, ...]) -> List[Tuple[int, int]]:
        """Reconstruct path from parent pointers."""
        path = []
        current = goal_state
        
        while parent[current] is not None:
            current, move = parent[current]
            path.append(move)
        
        path.reverse()
        return path

    def render(self, state: Tuple[int, ...]) -> None:
        """Render the current board state."""
        grid = [['.' for _ in range(self.size)] for _ in range(self.size)]
        
        for vid, v in enumerate(self.vehicles):
            r, c = state[vid << 1], state[(vid << 1) + 1]
            symbol = 'R' if vid == 0 else str(vid)
            
            for k in range(v.length):
                if v.horizontal:
                    grid[r][c + k] = symbol
                else:
                    grid[r + k][c] = symbol
        
        print('\n'.join(' '.join(row) for row in grid), end='\n\n')

    def get_statistics(self) -> Dict[str, int]:
        """Get current search statistics."""
        return {
            'nodes_expanded': self.nodes_expanded,
            'vehicles_count': len(self.vehicles),
            'board_size': self.size
        }

def load_level(path: str) -> Tuple[List[Vehicle], Tuple[int, ...]]:
    """Load a level from file."""
    vehicles = []
    
    try:
        with open(path, 'r') as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if len(parts) != 4:
                    continue
                    
                r, c, length, direction = parts
                vehicles.append(
                    Vehicle(idx, int(r), int(c), int(length), direction.upper() == 'H')
                )
    except FileNotFoundError:
        print(f"Error: Level file '{path}' not found.")
        sys.exit(1)
    except ValueError as e:
        print(f"Error parsing level file: {e}")
        sys.exit(1)
    
    if not vehicles:
        print("Error: No vehicles found in level file.")
        sys.exit(1)
    
    state = tuple(coord for v in vehicles for coord in (v.row, v.col))
    return vehicles, state

def benchmark_solver(board: Board, start_state: Tuple[int, ...], solver_name: str, solver_func, *args):
    """Benchmark a solver and return results."""
    print(f"\n=== {solver_name} ===")
    
    # Reset node counter
    board.nodes_expanded = 0
    
    # Memory tracking
    tracemalloc.start()
    start_current, start_peak = tracemalloc.get_traced_memory()
    
    # Time tracking
    start_time = time.time()
    
    # Run solver
    if args:
        result = solver_func(start_state, *args)
    else:
        result = solver_func(start_state)
    
    end_time = time.time()
    end_current, end_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Calculate metrics
    elapsed_time = end_time - start_time
    memory_used = (end_peak - start_current) / 1024  # KB
    
    if result is None:
        print("No solution found.")
        return None
    
    # Handle different return formats
    if isinstance(result, tuple) and len(result) == 2:
        # For UCS and A* that return (path, total_cost)
        path, total_cost = result
        print(f"Solution found in {len(path)} moves")
        print(f"Total cost: {total_cost}")
    else:
        # For other algorithms that return just the path
        path = result
        total_cost = sum(board.vehicles[vid].length for vid, _ in path)
        print(f"Solution found in {len(path)} moves")
        if solver_name in ['A* Search', 'A* Search (Simple)', 'Uniform-Cost Search']:
            print(f"Total cost: {total_cost}")
    
    print(f"Time: {elapsed_time:.4f}s")
    print(f"Memory: {memory_used:.2f} KB")
    print(f"Nodes expanded: {board.nodes_expanded}")
    
    return {
        'solver': solver_name,
        'moves': len(path),
        'total_cost': total_cost,
        'time': elapsed_time,
        'memory': memory_used,
        'nodes_expanded': board.nodes_expanded,
        'path': path
    }

def main():
    # Parse command line arguments
    level_file = sys.argv[1] if len(sys.argv) > 1 else 'level1.txt'
    algorithm = sys.argv[2] if len(sys.argv) > 2 else 'astar'
    
    # Load level
    vehicles, start_state = load_level(level_file)
    board = Board(vehicles)
    
    print(f"Loaded level: {level_file}")
    print(f"Vehicles: {len(vehicles)}")
    print("\nInitial state:")
    board.render(start_state)
    
    # Algorithm selection
    algorithms = {
        'bfs': ('Breadth-First Search', board.bfs_solver),
        'dfs': ('Depth-First Search', board.dfs_solver, 1000),
        'ucs': ('Uniform-Cost Search', board.ucs_solver),
        'astar': ('A* Search', board.astar, 'blocking'),
        'astar_simple': ('A* Search (Simple)', board.astar, 'manhattan'),
        'ids': ('Iterative Deepening Search', board.ids_solver, 50),
        'all': ('All Algorithms', None)
    }
    
    if algorithm == 'all':
        # Benchmark all algorithms
        results = []
        for alg_key, alg_info in algorithms.items():
            if alg_key == 'all':
                continue
            
            name, func = alg_info[0], alg_info[1]
            args = alg_info[2:] if len(alg_info) > 2 else []
            
            result = benchmark_solver(board, start_state, name, func, *args)
            if result:
                results.append(result)
        
        # Summary
        if results:
            print("\n=== SUMMARY ===")
            print(f"{'Algorithm':<25} {'Moves':<8} {'Cost':<8} {'Time(s)':<10} {'Memory(KB)':<12} {'Nodes':<10}")
            print("-" * 78)
            for r in results:
                print(f"{r['solver']:<25} {r['moves']:<8} {r['total_cost']:<8} {r['time']:<10.4f} {r['memory']:<12.2f} {r['nodes_expanded']:<10}")
    
    elif algorithm in algorithms:
        name, func = algorithms[algorithm][0], algorithms[algorithm][1]
        args = algorithms[algorithm][2:] if len(algorithms[algorithm]) > 2 else []
        
        result = benchmark_solver(board, start_state, name, func, *args)
        
        if result and result['path']:
            print(f"\nSolution steps:")
            state = start_state
            for step, (vid, delta) in enumerate(result['path'], 1):
                direction = '>' if delta > 0 and board.vehicles[vid].horizontal else \
                           '<' if delta < 0 and board.vehicles[vid].horizontal else \
                           'v' if delta > 0 and not board.vehicles[vid].horizontal else '^'
                
                vehicle_cost = board.vehicles[vid].length
                print(f"Step {step:2d}: Vehicle {vid} move {direction} (cost: {vehicle_cost})")
                state = board.move(state, vid, delta)
                board.render(state)
    else:
        print(f"Unknown algorithm: {algorithm}")
        print(f"Available algorithms: {', '.join(algorithms.keys())}")

if __name__ == '__main__':
    main()
