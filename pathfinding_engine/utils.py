# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part A: Single Player Freckers

from .core import Coord, CellState, BOARD_N, Direction
from typing import Callable


def apply_ansi(
    text: str, 
    bold: bool = False, 
    color: str | None = None
):
    """
    Wraps some text with ANSI control codes to apply terminal-based formatting.
    Note: Not all terminals will be compatible!
    """
    bold_code = "\033[1m" if bold else ""
    color_code = ""
    if color == "r":
        color_code = "\033[31m"
    if color == "b":
        color_code = "\033[34m"
    if color == "g":
        color_code = "\033[32m"
    return f"{bold_code}{color_code}{text}\033[0m"


def render_board(
    board: dict[Coord, CellState], 
    ansi: bool = False
) -> str:
    """
    Visualise the Tetress board via a multiline ASCII string, including
    optional ANSI styling for terminals that support this.

    If a target coordinate is provided, the token at that location will be
    capitalised/highlighted.
    """
    output = ""
    for r in range(BOARD_N):
        for c in range(BOARD_N):
            cell_state = board.get(Coord(r, c), None)
            if cell_state:
                text = '.'
                color = None
                if cell_state == CellState.RED:
                    text = "R"
                    color = "r"
                elif cell_state == CellState.BLUE:
                    text = "B"
                    color = "b"
                elif cell_state == CellState.LILY_PAD:
                    text = "*"
                    color = "g"

                if ansi:
                    output += apply_ansi(text, color=color)
                else:
                    output += text
            else:
                output += "."
            output += " "
        output += "\n"
    return output

def plus_no_wrap(coord: Coord, direction: Direction) -> Coord | None:
    """Add direction to coordinate without wrapping, return None if out of bounds."""
    r = coord.r + direction.r
    c = coord.c + direction.c
    if 0 <= r < BOARD_N and 0 <= c < BOARD_N:
        return Coord(r, c)
    return None

def get_upward_neighbors(coord: Coord, board: dict[Coord, CellState]) -> dict[Coord, Direction]:
    """Get all valid upward neighbors (including horizontal) of a coordinate."""
    neighbors = {}

    for direction in {Direction.Up, Direction.UpLeft, Direction.UpRight, Direction.Left, Direction.Right}:
        neighbor = plus_no_wrap(coord, direction)
        if neighbor and neighbor in board:
            neighbors[neighbor] = direction
    return neighbors

def get_downward_neighbors(coord: Coord, board: dict[Coord, CellState]) -> dict[Coord, Direction]:
    """Get all valid downward neighbors (including horizontal) of a coordinate."""
    neighbors = {}

    for direction in {Direction.Down, Direction.DownLeft, 
    Direction.DownRight, Direction.Left, Direction.Right}:
        neighbor = plus_no_wrap(coord, direction)
        if neighbor and neighbor in board:
            neighbors[neighbor] = direction
    return neighbors

def process_jumps_recursive(start_pos: Coord, curr_landing_pos: Coord, 
                            jump_path: list[Direction], board: dict[Coord, CellState],
                            update_callback: Callable, get_neighbors_func: Callable, 
                            visited_blue_frog: set[Coord]) -> None:
    """Recursively process all possible jumps from current position."""
    update_callback(start_pos, curr_landing_pos, jump_path)

    for neighbor, direction in get_neighbors_func(curr_landing_pos, board).items():
        if board[neighbor] == CellState.BLUE and neighbor not in visited_blue_frog:
            next_landing_pos = plus_no_wrap(neighbor, direction)

            if (next_landing_pos and next_landing_pos in board 
                and (board[next_landing_pos] == CellState.LILY_PAD 
                or board[next_landing_pos] == CellState.RED)):
                visited_blue_frog.add(neighbor)

                process_jumps_recursive(
                    start_pos=start_pos,
                    curr_landing_pos=next_landing_pos,
                    jump_path=jump_path + [direction],
                    board=board,
                    update_callback=update_callback,
                    get_neighbors_func=get_neighbors_func,
                    visited_blue_frog=visited_blue_frog.copy()
                )



def initiate_jump_processing(start_pos: Coord, blue_frog: Coord, initial_direction: Direction, 
                            board: dict[Coord, CellState], update_callback: Callable, 
                            get_neighbors_func: Callable) -> None:
    """Start processing jumps from a blue frog in given direction."""
    first_landing_pos = plus_no_wrap(blue_frog, initial_direction)

    if (first_landing_pos and
        first_landing_pos in board and
        (board[first_landing_pos] == CellState.LILY_PAD 
         or board[first_landing_pos] == CellState.RED)):

        visited_blue_frog = {blue_frog}

        process_jumps_recursive(
            start_pos=start_pos,
            curr_landing_pos=first_landing_pos,
            jump_path=[initial_direction],
            board=board,
            update_callback=update_callback,
            get_neighbors_func=get_neighbors_func,
            visited_blue_frog=visited_blue_frog
        )


