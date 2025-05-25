from .bitboard import Bitboard, PIECE_LILYPAD
from referee.game import PlayerColor, Coord, Action
import math

# a simple evaluation function
# the target row for the red team is y=7 (the 8th row)
# the target row for the blue team is y=0 (the 1st row)
RED_TARGET_ROW = 7
BLUE_TARGET_ROW = 0

def simple_evaluate(board: Bitboard, player_color: PlayerColor) -> float:
    """
    a simple evaluation function.
    evaluation logic: (the sum of the distance of the red frogs to the target row) - (the sum of the distance of the blue frogs to the target row)
    """
    score = 0.0

    if player_color == PlayerColor.RED:
        for coord in board.red_frog_coords:
            score -= RED_TARGET_ROW - coord.r
        for coord in board.blue_frog_coords:
            score += coord.r - BLUE_TARGET_ROW
    else: # player_color == PlayerColor.BLUE
        for coord in board.blue_frog_coords:
            score -= coord.r - BLUE_TARGET_ROW
        for coord in board.red_frog_coords:
            score += RED_TARGET_ROW - coord.r

    score += board.count_pieces(PIECE_LILYPAD) * 0.025
    
    return score

# transposition table (Transposition Table)
# the key is the hash value of the board state, and the value is (depth, score, flag, best_move)
# flag: 0 (exact value), 1 (alpha/lowerbound), 2 (beta/upperbound)
transposition_table = {}

def alpha_beta_search(
    current_board: Bitboard, 
    depth: int, 
    alpha: float, 
    beta: float, 
    maximizing_player_color: PlayerColor, # the current player who is making the decision
    eval_player_color: PlayerColor       # the player to evaluate
) -> tuple[float, Action | None]:
    """
    Alpha-Beta search function.
    return (evaluation score, best action)
    """
    board_hash = current_board.current_hash
    alpha_original = alpha # save the original alpha value, for transposition table storage

    # 1. transposition table lookup
    if board_hash in transposition_table:
        entry = transposition_table[board_hash]
        tt_depth, tt_score, tt_flag, tt_best_move = entry
        if tt_depth >= depth:
            if tt_flag == 0: # exact value
                return tt_score, tt_best_move
            elif tt_flag == 1: # alpha/lowerbound
                alpha = max(alpha, tt_score)
            elif tt_flag == 2: # beta/upperbound
                beta = min(beta, tt_score)
            
            if alpha >= beta: # the updated alpha-beta boundary causes pruning
                return tt_score, tt_best_move

    # 2. reach the leaf node or specified depth
    if depth == 0 or current_board.is_game_over():
        return simple_evaluate(current_board, eval_player_color), None

    best_move_for_this_node = None
    legal_moves = current_board.get_legal_moves(maximizing_player_color)

    if not legal_moves:
        # if there are no legal moves, it usually means the game is over or some special state
        return simple_evaluate(current_board, eval_player_color), None

    if maximizing_player_color == eval_player_color: # the current node is a Max node
        max_eval = -math.inf
        for move in legal_moves:
            next_board = current_board.clone()
            next_board.apply_action(maximizing_player_color, move)
            
            # recursive call
            opponent_color = PlayerColor.RED if maximizing_player_color == PlayerColor.BLUE else PlayerColor.BLUE
            current_eval, _ = alpha_beta_search(next_board, depth - 1, alpha, beta, opponent_color, eval_player_color)
            
            if current_eval > max_eval:
                max_eval = current_eval
                best_move_for_this_node = move
            alpha = max(alpha, current_eval)
            if beta <= alpha:
                break # Beta pruning
        
        # store to transposition table
        flag_to_store = 0 # default is exact value
        if max_eval <= alpha_original: # the real value <= max_eval
            flag_to_store = 2 # upperbound
        elif max_eval >= beta: # the real value >= max_eval (or >= beta)
            flag_to_store = 1 # lowerbound
        transposition_table[board_hash] = (depth, max_eval, flag_to_store, best_move_for_this_node)
        
        return max_eval, best_move_for_this_node
    else: # the current node is a Min node
        min_eval = math.inf
        for move in legal_moves:
            next_board = current_board.clone()
            next_board.apply_action(maximizing_player_color, move)

            opponent_color = PlayerColor.RED if maximizing_player_color == PlayerColor.BLUE else PlayerColor.BLUE
            current_eval, _ = alpha_beta_search(next_board, depth - 1, alpha, beta, opponent_color, eval_player_color)

            if current_eval < min_eval:
                min_eval = current_eval
                best_move_for_this_node = move
            beta = min(beta, current_eval)
            if beta <= alpha:
                break # Alpha pruning
        
        # store to transposition table
        flag_to_store = 0 # default is exact value
        if min_eval >= beta:
            flag_to_store = 1
        elif min_eval <= alpha_original:
            flag_to_store = 2
        transposition_table[board_hash] = (depth, min_eval, flag_to_store, best_move_for_this_node)

        return min_eval, best_move_for_this_node