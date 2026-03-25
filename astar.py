def get_neighbors(node, grid):
    neighbors = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] # UP, DOWN, LEFT, RIGHT
    for d in directions:
        nx, ny = node[0] + d[0], node[1] + d[1]
        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny] == 0:
            neighbors.append((nx, ny))
    return neighbors

def heuristic(a, b):
    # Manhattan distance heuristic
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(grid, start, goal):
    """
    A* algorithm implementation for the Trainer to find the shortest
    path to the Pokemon.
    Returns the path as a list of positions.
    """
    from queue import PriorityQueue
    queue = PriorityQueue()
    queue.put((0, start))
    
    came_from = {}
    g_score = {start: 0}
    
    while not queue.empty():
        current = queue.get()[1]
        
        # If we reached the goal, reconstruct the path
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
            
        for neighbor in get_neighbors(current, grid):
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal)
                queue.put((f_score, neighbor))
                
    return [] # Return empty if no path is found
