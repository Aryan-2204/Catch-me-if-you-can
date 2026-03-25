import random
from astar import astar
from minimax import get_best_escape_move

class Player:
    def __init__(self, start_pos):
        self.pos = start_pos
        self.prev_pos = start_pos
        self.speed_boost_turns = 0
        
    def apply_powerup(self, p_type):
        if p_type == "SPEED":
            self.speed_boost_turns = 5

class Pokemon:
    def __init__(self, start_pos, ai_type="MINIMAX"):
        self.pos = start_pos
        self.ai_type = ai_type  # "MINIMAX" or "ASTAR"
        self.freeze_turns = 0
        self.char_idx = random.randint(0, 3) # determines which sprite to use
        
    def get_move(self, player, grid, difficulty):
        if self.freeze_turns > 0:
            self.freeze_turns -= 1
            return self.pos
            
        target_pos = player.pos
        if self.ai_type == "SMART_MINIMAX" or (self.ai_type == "MINIMAX" and difficulty > 3):
            # Predict player movement
            dr = player.pos[0] - player.prev_pos[0]
            dc = player.pos[1] - player.prev_pos[1]
            pr = player.pos[0] + dr
            pc = player.pos[1] + dc
            if 0 <= pr < len(grid) and 0 <= pc < len(grid[0]) and grid[pr][pc] == 0:
                target_pos = (pr, pc)
            
        if self.ai_type == "ASTAR":
            # A* Pokemon escapes by running to the furthest corner
            furthest_corner = get_furthest_corner(target_pos, grid)
            path = astar(grid, self.pos, furthest_corner)
            if path and len(path) > 1:
                return path[1]
            else:
                # Fallback to random move
                r, c = self.pos
                neighbors = []
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == 0:
                        neighbors.append((nr, nc))
                return random.choice(neighbors) if neighbors else self.pos
        elif self.ai_type == "RANDOM":
            r, c = self.pos
            neighbors = []
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == 0:
                    neighbors.append((nr, nc))
            return random.choice(neighbors) if neighbors else self.pos
        else: # "MINIMAX"
            return get_best_escape_move(self.pos, target_pos, grid, depth=difficulty)

def get_furthest_corner(player_pos, grid):
    corners = [(1,1), (1, len(grid[0])-2), (len(grid)-2, 1), (len(grid)-2, len(grid[0])-2)]
    walkable_corners = [c for c in corners if grid[c[0]][c[1]] == 0]
    if not walkable_corners: return (1,1)
    
    furthest = walkable_corners[0]
    max_dist = -1
    for c in walkable_corners:
        dist = abs(c[0] - player_pos[0]) + abs(c[1] - player_pos[1])
        if dist > max_dist:
            max_dist = dist
            furthest = c
    return furthest

class Item:
    def __init__(self, pos, type_name):
        self.pos = pos
        self.type_name = type_name  # "SPEED", "FREEZE"
