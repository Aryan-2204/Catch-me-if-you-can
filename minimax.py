import math
import random
from astar import astar

MAX_DEPTH = 3

def get_valid_moves(pos, grid):
    moves = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)] # UP, DOWN, LEFT, RIGHT, STAY
    for d in directions:
        nx, ny = pos[0] + d[0], pos[1] + d[1]
        # Must stay on the grid and only walk on path (0)
        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny] == 0:
            moves.append((nx, ny))
    return moves

def eval_state(pokemon_pos, trainer_pos, grid):
    # Use A* to calculate TRUE maze distance, so Pikachu respects walls!
    path = astar(grid, pokemon_pos, trainer_pos)
    if not path and pokemon_pos != trainer_pos:
        return 999 # Safe, no path to Trainer
    return len(path)

def minimax(pokemon_pos, trainer_pos, depth, is_maximizing, grid):
    """
    Minimax search evaluating the best move for the Pokemon.
    Trainer is the minimizing player (wants distance = 0).
    Pokemon is the maximizing player (wants distance > 0).
    """
    # Base cases: Game over, or we have hit our maximum search depth
    if pokemon_pos == trainer_pos:
        # Caught! Pokemon prefers to delay this as much as possible.
        # Smaller depth means it survived deeper into the search tree.
        return -1000 - depth
        
    if depth == 0:
        return eval_state(pokemon_pos, trainer_pos, grid)
        
    if is_maximizing:
        # Pokemon's turn (Maximizing player)
        best_score = -math.inf
        for move in get_valid_moves(pokemon_pos, grid):
            best_score = max(best_score, minimax(move, trainer_pos, depth - 1, False, grid))
        return best_score
    else:
        # Trainer's turn (Minimizing player)
        best_score = math.inf
        for move in get_valid_moves(trainer_pos, grid):
            best_score = min(best_score, minimax(pokemon_pos, move, depth - 1, True, grid))
        return best_score

def get_best_escape_move(pokemon_pos, trainer_pos, grid, depth=3):
    """
    Returns the best move for the Pokemon by evaluating all valid immediate moves.
    """
    best_score = -math.inf
    best_moves = []
    
    for move in get_valid_moves(pokemon_pos, grid):
        # We start by testing each move, and pass the baton to the Trainer (False)
        score = minimax(move, trainer_pos, depth, False, grid)
        if score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)
            
    # Default fail-over if trapped
    if best_moves:
        best_move = random.choice(best_moves)
    else:
        valid_moves = get_valid_moves(pokemon_pos, grid)
        if valid_moves:
            best_move = random.choice(valid_moves)
        else:
            best_move = pokemon_pos # Can't move
            
    return best_move
