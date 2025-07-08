from dataclasses import dataclass
import heapq
from collections import deque

@dataclass(frozen=True)
class Vehicle:
    vehicleId: int       
    row: int             
    col: int             
    length: int          
    isHorizontal: bool   

class Board:
    def __init__(self, vehicles, size=6):
        self.vehicles = vehicles
        self.size = size
        self.nodesExpanded = 0

    def buildOccupied(self, state):
        occ = set()
        for vid, v in enumerate(self.vehicles):
            r, c = state[vid << 1], state[(vid << 1) + 1]  
            if v.isHorizontal:
                occ.update((r, c + k) for k in range(v.length))
            else:
                occ.update((r + k, c) for k in range(v.length))
        return occ

    def move(self, state, vid, delta):
        state_list = list(state)
        idx = vid << 1  
        if self.vehicles[vid].isHorizontal:
            state_list[idx + 1] += delta
        else:
            state_list[idx] += delta
        return tuple(state_list)

    def get_valid_moves(self, state, vid, occ) :
        moves = []
        v = self.vehicles[vid]
        r, c = state[vid << 1], state[(vid << 1) + 1]
        
        if v.isHorizontal:
            if c > 0 and (r, c - 1) not in occ:
                moves.append(-1)
            tail = c + v.length - 1
            if tail + 1 < self.size and (r, tail + 1) not in occ:
                moves.append(1)
        else:
            if r > 0 and (r - 1, c) not in occ:
                moves.append(-1)
            tail = r + v.length - 1
            if tail + 1 < self.size and (tail + 1, c) not in occ:
                moves.append(1)
        
        return moves

    def successors(self, state):
        succs = []
        occ = self.buildOccupied(state)
        
        for vid in range(len(self.vehicles)):
            moves = self.get_valid_moves(state, vid, occ)
            for delta in moves:
                new_state = self.move(state, vid, delta)
                succs.append((new_state, (vid, delta)))
        
        return succs

    def isGoal(self, state):
        red_col = state[1]
        red_tail = red_col + self.vehicles[0].length - 1
        return red_tail == self.size - 1

    
    def h(self, state):
        red_row, red_col = state[0], state[1]
        red_tail = red_col + self.vehicles[0].length - 1
        gap = (self.size - 1) - red_tail
        blocks = 0
        for vid, v in enumerate(self.vehicles[1:], 1):
            if v.isHorizontal: 
                continue
            c = state[vid * 2 + 1]
            if c == red_tail + 1:
                r = state[vid * 2]
                if r <= red_row < r + v.length:
                    blocks += 1
        return gap + 2 * blocks

    def aStar(self, start_state, heuristic='blocking'):
        h_func = self.h  
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
                g_next = g_cur + 1  
                if g_next < g_cost.get(next_state, float('inf')):
                    g_cost[next_state] = g_next
                    parent[next_state] = (current, move)
                    f_next = g_next + h_func(next_state)
                    heapq.heappush(pq, (f_next, g_next, next_state))

        return None

    def bfs(self, start_state):
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

    def ucs(self, start_state):
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


    def ids(self, start_state, max_depth = 300):
        self.nodesExpanded = 0  

        for depth_limit in range(max_depth):
            visited = {}
            parent = {start_state: None}
            found = self._dls_recursive(start_state, depth_limit, 0, visited, parent)
            if found:
                return self._reconstruct_path(parent, found)
        return None


    def _dls_recursive(self,state,depth_limit,depth,visited,parent):

        if state in visited:
            return None

        visited[state] = depth
        self.nodesExpanded += 1

        if self.isGoal(state):
            return state

        if depth < depth_limit:
            for s2, move in self.successors(state):
                if s2 not in visited or visited[s2] > depth + 1:
                    parent[s2] = (state, move)
                    found = self._dls_recursive(s2, depth_limit, depth + 1, visited, parent)
                    if found:
                        return found
        return None

    def _dfs_limited(self, start_state, depth_limit):
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
    def _reconstruct_path(parent, goal_state):
        path = []
        current = goal_state
        
        while parent[current] is not None:
            current, move = parent[current]
            path.append(move)
        
        path.reverse()
        return path

    def reconstruct(self, parent, state):
        return self._reconstruct_path(parent, state)

    def successorsBfs(self, state):
        return self.successors(state)

    def heuristic(self, state):
        return self.blocking_vehicles_heuristic(state)
