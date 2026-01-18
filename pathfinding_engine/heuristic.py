# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part A: Single Player Freckers
# implementation of the heuristic function

from .core import CellState, Coord, BOARD_N, Direction
from collections import deque
from .utils import get_upward_neighbors, initiate_jump_processing

class FreckersHeuristic:
    """
    Heuristic function for A* search that estimates distance to goal.
    Uses backward BFS from goal positions to precompute distances.
    """
    def __init__(self, board: dict[Coord, CellState]):
        """Initialize with board state and precompute distances."""
        self.distance_table: dict[Coord, float] = {}
        self._preprocess_board(board)

    def _preprocess_board(self, board: dict[Coord, CellState]) -> None:
        """
        Precompute distances from each cell to goal using backward BFS.
        Goal positions are lily pads in the bottom row.
        """
        queue = deque()
        visited = set()

        # Add lily pad positions from the bottom row to queue
        for c in range(BOARD_N):
            coord = Coord(BOARD_N-1, c)
            if coord in board and board[coord] == CellState.LILY_PAD:
                queue.append(coord)
                visited.add(coord)
                self.distance_table[coord] = 0

        def heuristic_update_callback(start_pos: Coord, landing_pos: Coord, direction: list[Direction]) -> None:
            """Update distance table when a valid jump is found."""
            new_distance = self.distance_table[start_pos] + 1

            if landing_pos not in visited:
                self.distance_table[landing_pos] = new_distance
                queue.append(landing_pos)
                visited.add(landing_pos)

        # Backward BFS from goal positions
        while queue:
            current = queue.popleft()
            current_distance = self.distance_table[current]
            
            # Process all upward neighbors
            for neighbor, direction in get_upward_neighbors(current, board).items():
                neighbor_state = board.get(neighbor)

                # Handle lily pad or red frog (single step)
                if neighbor_state == CellState.LILY_PAD or neighbor_state == CellState.RED:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_distance = current_distance + 1
                        self.distance_table[neighbor] = new_distance
                        queue.append(neighbor)
                
                # Handle blue frog (jump)
                elif neighbor_state == CellState.BLUE:
                    initiate_jump_processing(
                        start_pos=current,
                        blue_frog=neighbor,
                        initial_direction=direction,
                        board=board,
                        update_callback=heuristic_update_callback,
                        get_neighbors_func=get_upward_neighbors
                    )

    def estimate(self, curr_pos: Coord) -> float:
        """Return precomputed distance to goal for given position."""
        return self.distance_table.get(curr_pos, float('inf'))



