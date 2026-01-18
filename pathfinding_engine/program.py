# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part A: Single Player Freckers

from .core import CellState, Coord, Direction, MoveAction, BOARD_N
from .utils import render_board, get_downward_neighbors, initiate_jump_processing
from .heuristic import FreckersHeuristic
import heapq
from itertools import count

def search(
    board: dict[Coord, CellState]
) -> list[MoveAction] | None:
    """
    This is the entry point for your submission. You should modify this
    function to solve the search problem discussed in the Part A specification.
    See `core.py` for information on the types being used here.

    Parameters:
        `board`: a dictionary representing the initial board state, mapping
            coordinates to "player colours". The keys are `Coord` instances,
            and the values are `CellState` instances which can be one of
            `CellState.RED`, `CellState.BLUE`, or `CellState.LILY_PAD`.
    
    Returns:
        A list of "move actions" as MoveAction instances, or `None` if no
        solution is possible.
    """

    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!
    print(render_board(board, ansi=True))

    # initialize the heuristic table
    heuristic = FreckersHeuristic(board)

    # Priority queue for open set
    open_set = []
    g_dist = {} # Store g_scores (actual cost)
    f_dist = {} # Store f_scores (g_score + heuristic)
    curr_path = []
    counter = count()
    
    # Find initial red frog position
    start_pos = None
    for coord, state in board.items():
        if state == CellState.RED:
            start_pos = coord
            break
    
    if start_pos is None: 
        return None
    
    # Initialize start node
    g_dist[start_pos] = 0
    h_start = heuristic.estimate(start_pos)
    if h_start == float('inf'): 
        return None # No path to goal
    
    f_dist[start_pos] = g_dist[start_pos] + h_start
    heapq.heappush(open_set, (f_dist[start_pos], g_dist[start_pos], next(counter), start_pos, curr_path))

    def astar_update_callback(start_jump_pos, landing_pos, direction_list):
        """Update priority queue when a valid jump is found."""
        new_g = g_dist[start_jump_pos] + 1

        if landing_pos not in g_dist or new_g < g_dist[landing_pos]:
            g_dist[landing_pos] = new_g
            f_dist[landing_pos] = new_g + heuristic.estimate(landing_pos)

            action = MoveAction(start_jump_pos, direction_list)
            new_path = curr_path + [action]
            heapq.heappush(open_set, (f_dist[landing_pos], g_dist[landing_pos], next(counter), landing_pos, new_path))

    # main loop
    while open_set:
        _, curr_g, _, curr_pos, curr_path = heapq.heappop(open_set)

        # Since heuristic function is consistent, 
        # if we've reached the goal, immediately return the path
        if curr_pos.r == BOARD_N - 1:
            return curr_path
        
        # Explore neighbors
        for neighbor, direction in get_downward_neighbors(curr_pos, board).items():
            if board[neighbor] == CellState.LILY_PAD:
                new_g = curr_g + 1
                if neighbor not in g_dist or new_g < g_dist[neighbor]:
                    g_dist[neighbor] = new_g
                    f_dist[neighbor] = new_g + heuristic.estimate(neighbor)

                    action = MoveAction(curr_pos, [direction])
                    new_path = curr_path + [action]
                    heapq.heappush(open_set, (f_dist[neighbor], g_dist[neighbor], next(counter), neighbor, new_path))
            elif board[neighbor] == CellState.BLUE:
                initiate_jump_processing(
                    start_pos=curr_pos,
                    blue_frog=neighbor,
                    initial_direction=direction,
                    board=board,
                    update_callback=astar_update_callback,
                    get_neighbors_func=get_downward_neighbors
                )
    
    return None
        
    
    # Here we're returning "hardcoded" actions as an example of the expected
    # output format. Of course, you should instead return the result of your
    # search algorithm. Remember: if no solution is possible for a given input,
    # return `None` instead of a list.
    #return [
    #    MoveAction(Coord(0, 5), [Direction.Down]),
    #    MoveAction(Coord(1, 5), [Direction.DownLeft]),
    #    MoveAction(Coord(3, 3), [Direction.Left]),
    #    MoveAction(Coord(3, 2), [Direction.Down, Direction.Right]),
    #    MoveAction(Coord(5, 4), [Direction.Down]),
    #    MoveAction(Coord(6, 4), [Direction.Down]),
    #]
