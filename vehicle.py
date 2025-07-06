from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Set
import heapq
import tracemalloc
import time
from collections import deque

@dataclass(frozen=True)
class Vehicle:
    vehicleId: int        # ID (0 = xe đỏ)
    row: int             # hàng ô đầu
    col: int             # cột ô đầu
    length: int          # chiều dài (2 hoặc 3)
    isHorizontal: bool   # True = ngang, False = dọc

class Board:
    def __init__(self, vehicles: List[Vehicle], size: int = 6) -> None:
        self.vehicles = vehicles
        self.size = size
        self.nodesExpanded = 0

    def buildOccupied(self, state: Tuple[int, ...]) -> Set[Tuple[int, int]]:
        """Build set of occupied cells from current state."""
        occ = set()
        for vid, v in enumerate(self.vehicles):
            r, c = state[vid << 1], state[(vid << 1) + 1]  # Bit shift instead of multiplication
            if v.isHorizontal:
                occ.update((r, c + k) for k in range(v.length))
            else:
                occ.update((r + k, c) for k in range(v.length))
        return occ

    def move(self, state: Tuple[int, ...], vid: int, delta: int) -> Tuple[int, ...]:
        """Create new state by moving vehicle vid by delta positions."""
        state_list = list(state)
        idx = vid << 1  # Bit shift for vid * 2
        if self.vehicles[vid].isHorizontal:
            state_list[idx + 1] += delta
        else:
            state_list[idx] += delta
        return tuple(state_list)

    def get_valid_moves(self, state: Tuple[int, ...], vid: int, occ: Set[Tuple[int, int]]) -> List[int]:
        """Get all valid moves for a specific vehicle."""
        moves = []
        v = self.vehicles[vid]
        r, c = state[vid << 1], state[(vid << 1) + 1]
        
        if v.isHorizontal:
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
        occ = self.buildOccupied(state)
        
        for vid in range(len(self.vehicles)):
            moves = self.get_valid_moves(state, vid, occ)
            for delta in moves:
                new_state = self.move(state, vid, delta)
                succs.append((new_state, (vid, delta)))
        
        return succs

    def isGoal(self, state: Tuple[int, ...]) -> bool:
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
            if not v.isHorizontal:  # Only vertical vehicles can block
                c = state[(vid << 1) + 1]
                # Check if this vehicle is in the red car's path
                if red_tail < c <= self.size - 1:
                    r = state[vid << 1]
                    # Check if it overlaps with red car's row
                    if r <= red_row < r + v.length:
                        blocks += 1
        
        return gap + blocks

    def aStar(self, start_state: Tuple[int, ...], heuristic: str = 'blocking') -> Optional[Tuple[List[Tuple[int, int]], int]]:
        """A* search implementation with selectable heuristic."""
        h_func = self.blocking_vehicles_heuristic if heuristic == 'blocking' else self.manhattan_distance_heuristic
        
        g_cost = {start_state: 0}
        pq = [(h_func(start_state), 0, start_state)]
        parent = {start_state: None}
        self.nodesExpanded = 0
        
        while pq:
            f, g_cur, current = heapq.heappop(pq)
            
            if g_cur > g_cost.get(current, float('inf')):
                continue
                
            self.nodesExpanded += 1
            
            if self.isGoal(current):
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

    def bfs(self, start_state: Tuple[int, ...]) -> Optional[List[Tuple[int, int]]]:
        """Breadth-First Search implementation."""
        queue = deque([start_state])
        parent = {start_state: None}
        visited = {start_state}
        self.nodesExpanded = 0
        
        while queue:
            current = queue.popleft()
            self.nodesExpanded += 1
            
            if self.isGoal(current):
                return self._reconstruct_path(parent, current)
            
            for next_state, move in self.successors(current):
                if next_state not in visited:
                    visited.add(next_state)
                    parent[next_state] = (current, move)
                    queue.append(next_state)
        
        return None

    def ucs(self, start_state: Tuple[int, ...]) -> Optional[Tuple[List[Tuple[int, int]], int]]:
        """Uniform-Cost Search implementation."""
        g_cost = {start_state: 0}
        pq = [(0, start_state)]
        parent = {start_state: None}
        self.nodesExpanded = 0
        
        while pq:
            cost, current = heapq.heappop(pq)
            
            if cost > g_cost.get(current, float('inf')):
                continue
                
            self.nodesExpanded += 1
            
            if self.isGoal(current):
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

    def ids(self, start_state: Tuple[int, ...], max_depth: int = 100) -> Optional[List[Tuple[int, int]]]:
        """Iterative Deepening Search implementation."""
        for depth_limit in range(max_depth + 1):
            self.nodesExpanded = 0
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
            self.nodesExpanded += 1
            
            if self.isGoal(current):
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

    # Legacy methods for backward compatibility
    def reconstruct(self, parent, state):
        """Legacy method for backward compatibility."""
        return self._reconstruct_path(parent, state)

    def successorsBfs(self, state: Tuple[int, ...]):
        """Legacy method for backward compatibility."""
        return self.successors(state)

    def heuristic(self, state: Tuple[int, ...]) -> int:
        """Legacy method for backward compatibility."""
        return self.blocking_vehicles_heuristic(state)
