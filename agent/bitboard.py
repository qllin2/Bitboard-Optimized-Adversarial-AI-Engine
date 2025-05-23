# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Coord, Direction, Action, MoveAction, GrowAction, constants
import random
import collections

BOARD_SIZE = constants.BOARD_N
MAX_TURNS = constants.MAX_TURNS

# define the piece types
PIECE_RED = 0    # red frog
PIECE_BLUE = 1   # blue frog
PIECE_LILYPAD = 2 # lilypad

# the target row for the red team is y=7 (the 8th row)
# the target row for the blue team is y=0 (the 1st row)
RED_TARGET_ROW = 7
BLUE_TARGET_ROW = 0

class Bitboard:
    """
    Use Bitboard to represent the board state of Freckers game.
    Bitboard is an efficient way to represent the board state using binary bits.
    """
    
    ZOBRIST_TABLE = None # Class variable for the Zobrist hash table
    
    def __init__(self, player_color: PlayerColor) -> None:
        """initialize an empty Bitboard"""
        # initialize the Zobrist hash table
        Bitboard._init_zobrist_table()
        
        # initialize five bitboards: red frogs, blue frogs, and lilypads and two potential lilypads bitboards
        self.red_frogs = 0
        self.blue_frogs = 0
        self.lilypads = 0
        
        self.red_frog_coords = set()
        self.blue_frog_coords = set()
        # the current Zobrist hash value
        self.current_hash = 0
        self.player_color = player_color
        self.turns = 1 if player_color == PlayerColor.RED else 2
    
    @classmethod
    def _init_zobrist_table(cls) -> None:
        """initialize the Zobrist hash table, for efficient comparison of board states"""
        if cls.ZOBRIST_TABLE is None:
            cls.ZOBRIST_TABLE = [[[random.getrandbits(64) for _ in range(3)]
                                for _ in range(BOARD_SIZE)]
                                for _ in range(BOARD_SIZE)]
        
    def setup_initial_position(self) -> None:
        """set the initial position of the game"""
        # clear all bitboards
        self.red_frogs = 0
        self.blue_frogs = 0
        self.lilypads = 0
        self.current_hash = 0
        self.red_frog_coords.clear()
        self.blue_frog_coords.clear()
        self.turns = 0
        
        # set the red frogs: the first row, from column 2 to 7
        for c in range(1, 7):
            self.set_piece(0, c, PIECE_RED)

        # set the blue frogs: the last row, from column 2 to 7
        for c in range(1, 7):
            self.set_piece(7, c, PIECE_BLUE)
        
        # set the lilypads
        self.set_piece(0, 0, PIECE_LILYPAD)
        self.set_piece(0, 7, PIECE_LILYPAD)
        
        for c in range(1, 7):
            self.set_piece(1, c, PIECE_LILYPAD)
            self.set_piece(6, c, PIECE_LILYPAD)
        
        self.set_piece(7, 0, PIECE_LILYPAD)
        self.set_piece(7, 7, PIECE_LILYPAD)
        
    def get_bit(self, bitboard: int, row: int, col: int) -> int:
        """get the bit value at the specified position"""
        index = row * BOARD_SIZE + col
        return (bitboard >> index) & 1
    
    def set_bit(self, bitboard: int, row: int, col: int) -> int:
        """set the bit at the specified position to 1"""
        index = row * BOARD_SIZE + col
        return bitboard | (1 << index)
    
    def clear_bit(self, bitboard: int, row: int, col: int) -> int:
        """clear the bit at the specified position"""
        index = row * BOARD_SIZE + col
        return bitboard & ~(1 << index)
    
    def is_empty(self, row: int, col: int) -> bool:
        """check if the specified position is empty"""
        return not (self.get_bit(self.red_frogs, row, col) or 
                   self.get_bit(self.blue_frogs, row, col) or
                   self.get_bit(self.lilypads, row, col))
    
    def has_lilypad(self, row: int, col: int) -> bool:
        """check if the specified position has a lilypad"""
        return self.get_bit(self.lilypads, row, col) == 1
    
    def get_piece(self, row: int, col: int) -> int:
        """get the piece type at the specified position"""
        if self.get_bit(self.red_frogs, row, col):
            return PIECE_RED
        if self.get_bit(self.blue_frogs, row, col):
            return PIECE_BLUE
        if self.get_bit(self.lilypads, row, col):
            return PIECE_LILYPAD
        return None

    def remove_piece(self, row: int, col: int) -> None:
        """remove the piece at the specified position"""
        piece = self.get_piece(row, col)
        if piece == PIECE_RED:
            self.red_frog_coords.remove(Coord(row, col))
            self.red_frogs = self.clear_bit(self.red_frogs, row, col)
            self.current_hash ^= Bitboard.ZOBRIST_TABLE[row][col][PIECE_RED]
        elif piece == PIECE_BLUE:
            self.blue_frog_coords.remove(Coord(row, col))
            self.blue_frogs = self.clear_bit(self.blue_frogs, row, col)
            self.current_hash ^= Bitboard.ZOBRIST_TABLE[row][col][PIECE_BLUE]
        elif piece == PIECE_LILYPAD:
            self.lilypads = self.clear_bit(self.lilypads, row, col)
            self.current_hash ^= Bitboard.ZOBRIST_TABLE[row][col][PIECE_LILYPAD]

    def set_piece(self, row: int, col: int, piece_type: int) -> None:
        """set a piece at the specified position"""
        # first update the hash value, by XORing the current position's all piece information
        old_piece = self.get_piece(row, col)
        if old_piece is not None:
            self.remove_piece(row, col)
        
        # set the new piece
        if piece_type == PIECE_RED:
            self.red_frogs = self.set_bit(self.red_frogs, row, col)
            self.current_hash ^= Bitboard.ZOBRIST_TABLE[row][col][PIECE_RED]
            self.red_frog_coords.add(Coord(row, col))
        elif piece_type == PIECE_BLUE:
            self.blue_frogs = self.set_bit(self.blue_frogs, row, col)
            self.current_hash ^= Bitboard.ZOBRIST_TABLE[row][col][PIECE_BLUE]
            self.blue_frog_coords.add(Coord(row, col))
        elif piece_type == PIECE_LILYPAD:
            self.lilypads = self.set_bit(self.lilypads, row, col)
            self.current_hash ^= Bitboard.ZOBRIST_TABLE[row][col][PIECE_LILYPAD]
    
    def move_piece(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """move the piece from the specified position to the target position"""
        piece = self.get_piece(from_row, from_col)
        if piece not in [PIECE_RED, PIECE_BLUE]:
            return False  # this piece is not movable
            
        # check if the target position has a lilypad
        if not self.has_lilypad(to_row, to_col):
            return False
            
        # move the piece
        self.remove_piece(from_row, from_col)
        self.set_piece(to_row, to_col, piece)
            
        return True

    def grow_lilypads(self, color: PlayerColor) -> bool:
        """grow the lilypads around the frogs"""
        changes = 0
        if color == PlayerColor.RED:
            frog_coords = self.red_frog_coords
        else:
            frog_coords = self.blue_frog_coords

        for coord in frog_coords:
            row, col = coord.r, coord.c
            
            # check the 8 directions
            for direction in Direction:
                dr, dc = self._direction_to_offset(direction)
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                    if self.is_empty(new_row, new_col):
                        self.set_piece(new_row, new_col, PIECE_LILYPAD)
                        changes += 1
        return changes > 0
    
    def get_legal_moves(self, color: PlayerColor) -> list[Action]:
        """get all legal moves for the current player"""
        legal_moves = []
        frogs_bb = self.red_frogs if color == PlayerColor.RED else self.blue_frogs
        
        # define movement directions based on player color
        if color == PlayerColor.RED:
            # Red frogs: Down, DownLeft, DownRight, Left, Right
            move_directions = [Direction.Down, Direction.DownLeft, Direction.DownRight, Direction.Left, Direction.Right]
            frog_coords = self.red_frog_coords
        else:  # PlayerColor.BLUE
            # Blue frogs: Up, UpLeft, UpRight, Left, Right
            move_directions = [Direction.Up, Direction.UpLeft, Direction.UpRight, Direction.Left, Direction.Right]
            frog_coords = self.blue_frog_coords
        
        for coord in frog_coords:
            r, c = coord.r, coord.c   
            original_frog_coord = Coord(r, c)     
            jump_q = collections.deque() # Queue for BFS for this specific frog's jumps

            # Iterate through possible directions for single steps or initial jumps
            for direction in move_directions:
                dr, dc = self._direction_to_offset(direction)
                
                # First position in the direction
                step_r, step_c = r + dr, c + dc

                if 0 <= step_r < BOARD_SIZE and 0 <= step_c < BOARD_SIZE:
                    # Case 1: Single step to a lilypad
                    if self.has_lilypad(step_r, step_c):
                        legal_moves.append(MoveAction(original_frog_coord, [direction]))
                    
                    # Case 2: Potential jump over another frog (any color)
                    elif (self.get_bit(self.red_frogs, step_r, step_c) or \
                            self.get_bit(self.blue_frogs, step_r, step_c)):
                        
                        # Landing position after the jump
                        land_r, land_c = step_r + dr, step_c + dc

                        if (0 <= land_r < BOARD_SIZE and 0 <= land_c < BOARD_SIZE and
                            self.has_lilypad(land_r, land_c)):
                            
                            # This is a valid first jump
                            initial_jump_path = [direction]
                            legal_moves.append(MoveAction(original_frog_coord, list(initial_jump_path)))
                            visited_positions = set([(r, c), (land_r, land_c)])
                            jump_q.append(((land_r, land_c), initial_jump_path, visited_positions))
            
            # Continue BFS for chained jumps for the current frog
            while jump_q:
                (current_pos_tuple, path_so_far_list, visited_positions) = jump_q.popleft()
                curr_r_jump, curr_c_jump = current_pos_tuple

                for next_direction_jump in move_directions:
                    dr_next, dc_next = self._direction_to_offset(next_direction_jump)
                    
                    jump_over_r_next, jump_over_c_next = curr_r_jump + dr_next, curr_c_jump + dc_next
                    if not ((0 <= jump_over_r_next < BOARD_SIZE and 0 <= jump_over_c_next < BOARD_SIZE) and \
                            (self.get_bit(self.red_frogs, jump_over_r_next, jump_over_c_next) or \
                            self.get_bit(self.blue_frogs, jump_over_r_next, jump_over_c_next))):
                        continue
                    land_r_next, land_c_next = jump_over_r_next + dr_next, jump_over_c_next + dc_next
                    if not ((0 <= land_r_next < BOARD_SIZE and 0 <= land_c_next < BOARD_SIZE) and \
                        self.has_lilypad(land_r_next, land_c_next)):
                        continue

                    # Check for invalid landings
                    if (land_r_next, land_c_next) in visited_positions: # Cannot land on a previous spot in this jump sequence
                        continue
                    
                    new_path_dirs = list(path_so_far_list) 
                    new_path_dirs.append(next_direction_jump)

                    # Create a copy of visited_positions for the new path branch
                    new_visited_for_next_branch = visited_positions.copy()
                    new_visited_for_next_branch.add((land_r_next, land_c_next))
                    
                    jump_q.append(((land_r_next, land_c_next), new_path_dirs, new_visited_for_next_branch))
                    legal_moves.append(MoveAction(original_frog_coord, list(new_path_dirs))) 
        
        legal_moves.append(GrowAction())
        return legal_moves
    
    def _direction_to_offset(self, direction: Direction) -> tuple[int, int]:
        """convert direction to row and column offset"""
        match direction:
            case Direction.Up:
                return (-1, 0)
            case Direction.Down:
                return (1, 0)
            case Direction.Left:
                return (0, -1)
            case Direction.Right:
                return (0, 1)
            case Direction.UpLeft:
                return (-1, -1)
            case Direction.UpRight:
                return (-1, 1)
            case Direction.DownLeft:
                return (1, -1)
            case Direction.DownRight:
                return (1, 1)
    
    def apply_action(self, color: PlayerColor, action: Action) -> bool:
        """apply an action to the board"""
        if isinstance(action, MoveAction):
            coord, directions = action.coord, action.directions
            curr_row, curr_col = coord.r, coord.c
            
            # get the piece at the current position
            piece = self.get_piece(curr_row, curr_col)
            
            # check if the selected piece is the correct color
            if (color == PlayerColor.RED and piece != PIECE_RED) or \
               (color == PlayerColor.BLUE and piece != PIECE_BLUE):
                return False
            
            if len(directions) == 0:
                return False
            
            # if the action is a jump action sequence
            if len(directions) > 1:
                target_row, target_col = curr_row, curr_col
                for direction_segment in directions: 
                    dr, dc = self._direction_to_offset(direction_segment)
                    target_row += 2 * dr 
                    target_col += 2 * dc
                if not self.move_piece(curr_row, curr_col, target_row, target_col):
                    return False
                self.turns += 1
                return True # Successfully moved
            
            # single direction in the list: could be a 1-square step or a 2-square jump
            elif len(directions) == 1:
                dr, dc = self._direction_to_offset(directions[0])
                if self.has_lilypad(curr_row + dr, curr_col + dc):
                    # single step
                    target_row, target_col = curr_row + dr, curr_col + dc
                else:
                    # jump
                    target_row, target_col = curr_row + 2 * dr, curr_col + 2 * dc
                if not self.move_piece(curr_row, curr_col, target_row, target_col):
                    return False
                self.turns += 1
                return True
        elif isinstance(action, GrowAction):
            if self.grow_lilypads(color):
                self.turns += 1
                return True
        return False
    
    def count_set_bits(self, bitboard: int) -> int:
        """count the number of set bits in the bitboard"""
        count = 0
        while bitboard:
            bitboard &= bitboard - 1
            count += 1
        return count
    
    def count_pieces(self, piece_type: int) -> int:
        """count the number of pieces of the specified type"""
        if piece_type == PIECE_RED:
            return self.count_set_bits(self.red_frogs)
        elif piece_type == PIECE_BLUE:
            return self.count_set_bits(self.blue_frogs)
        elif piece_type == PIECE_LILYPAD:
            return self.count_set_bits(self.lilypads)
        return 0
    
    def __str__(self) -> str:
        """convert the board to a readable string"""
        result = []
        for row in range(BOARD_SIZE):
            row_str = []
            for col in range(BOARD_SIZE):
                piece = self.get_piece(row, col)
                if piece == PIECE_RED:
                    row_str.append('R')
                elif piece == PIECE_BLUE:
                    row_str.append('B')
                elif piece == PIECE_LILYPAD:
                    row_str.append('*')
                else:
                    row_str.append('.')
            result.append(' '.join(row_str))
        return '\n'.join(result)
    
    def clone(self) -> 'Bitboard':
        """create a complete copy of the current board state"""
        copy = Bitboard(self.player_color)
        copy.red_frogs = self.red_frogs
        copy.blue_frogs = self.blue_frogs
        copy.lilypads = self.lilypads
        copy.current_hash = self.current_hash
        copy.red_frog_coords = self.red_frog_coords.copy()
        copy.blue_frog_coords = self.blue_frog_coords.copy()
        copy.turns = self.turns
        # no need to copy zobrist_table, it is the same for all instances
        return copy

    def is_game_over(self) -> bool:
        """
        Checks if the game has reached a terminal state where a player has lost
        by running out of frogs.
        """
        if self.turns >= MAX_TURNS:
            return True
        if self.get_winner() is not None:
            return True
        return False
    
    def get_winner(self) -> PlayerColor:
        """get the winner of the game"""
        if all(coord.r == 7 for coord in self.red_frog_coords):
            return PlayerColor.RED
        if all(coord.r == 0 for coord in self.blue_frog_coords):
            return PlayerColor.BLUE
        return None

    def get_game_phase(self) -> str:
        my_frogs = self.red_frog_coords if self.player_color == PlayerColor.RED else self.blue_frog_coords
        
        my_progress_values = []
        for coords in my_frogs:
            my_progress_values.append(coords.r if self.player_color == PlayerColor.RED else (BOARD_SIZE - 1 - coords.r))
        my_progress_avg = sum(my_progress_values) / len(my_progress_values)

        EARLY_GAME_TURN = 20
        LATE_GAME_TURN = 30
        avg_progress_mid_threshold = (BOARD_SIZE - 1) * 0.25
        avg_progress_late_threshold = (BOARD_SIZE - 1) * 0.65
        near_target_count = 0

        if self.turns < EARLY_GAME_TURN or my_progress_avg < avg_progress_mid_threshold:
            return "EARLY"
        
        if self.turns > LATE_GAME_TURN or my_progress_avg > avg_progress_late_threshold:
            target_r = RED_TARGET_ROW if self.player_color == PlayerColor.RED else BLUE_TARGET_ROW
            for coord in my_frogs:
                if self.player_color == PlayerColor.RED and coord.r >= target_r - 1:
                    near_target_count += 1
                if self.player_color == PlayerColor.BLUE and coord.r <= target_r + 1:
                    near_target_count += 1
            if near_target_count >= 2:
                return "LATE"
            if self.turns > LATE_GAME_TURN:
                return "MID_LATE"
        
        return "MID"
