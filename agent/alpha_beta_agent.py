from .bitboard import Bitboard, PIECE_LILYPAD
from referee.game import PlayerColor, Coord, Action, constants
import math

BOARD_N = constants.BOARD_N
EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2

def evaluate_board(board: Bitboard, player_color: PlayerColor) -> float:
    """
    a evaluation function.
    """
    if board.get_winner() is not None:
        if board.get_winner() == player_color:
            return math.inf
        else:
            return -math.inf
    if board.is_game_over() and board.get_winner() is None: # draw
        return 0.0
    
    my_color = player_color

    if player_color == PlayerColor.RED:
        W_PROGRESSION = 10
        W_OPPONENT_PROGRESSION = -3
        W_MOBILITY = 0.25
        W_STRAGGLER = -5
    else:
        W_PROGRESSION = 10
        W_OPPONENT_PROGRESSION = -8
        W_MOBILITY = 0.25
        W_STRAGGLER = -5

    w_progression = W_PROGRESSION
    w_opponent_progression = W_OPPONENT_PROGRESSION
    w_mobility = W_MOBILITY
    w_straggler = W_STRAGGLER

    opponent_color = PlayerColor.RED if player_color == PlayerColor.BLUE else PlayerColor.BLUE
    # frog progression advantage
    my_frog_score = 0.0
    opponent_frog_score = 0.0
    my_frogs = board.red_frog_coords if my_color == PlayerColor.RED else board.blue_frog_coords
    opponent_frogs = board.blue_frog_coords if my_color == PlayerColor.RED else board.red_frog_coords
    for coord in my_frogs:
        my_frog_score += coord.r if my_color == PlayerColor.RED else (BOARD_N - 1 - coord.r)
    for coord in opponent_frogs:
        opponent_frog_score += coord.r if my_color == PlayerColor.BLUE else (BOARD_N - 1 - coord.r)  

    # frog mobility advantage
    my_mobility = len(board.get_legal_moves(my_color))
    opponent_mobility = len(board.get_legal_moves(opponent_color))
    mobility_advantage = my_mobility - opponent_mobility

    # frog straggler penalty
    straggler_penalty = 0
    my_progression = []
    for coord in my_frogs:
        my_progression.append(coord.r if my_color == PlayerColor.RED else (BOARD_N - 1 - coord.r))
    my_progression_avg = sum(my_progression) / len(my_progression)
    my_progression_std = math.sqrt(sum((x - my_progression_avg) ** 2 for x in my_progression) / len(my_progression))
    straggler_penalty = my_progression_std

    # weighted sum
    final_score = (w_progression * my_frog_score) + \
        (w_opponent_progression * opponent_frog_score) + \
        (w_mobility * mobility_advantage) + \
        (w_straggler * straggler_penalty)

    return final_score


def alpha_beta_search(
    current_board: Bitboard, 
    depth: int, 
    alpha: float, 
    beta: float, 
    maximizing_player_color: PlayerColor, # the current player who is making the decision
    eval_player_color: PlayerColor,       # the player to evaluate
    transposition_table: dict
) -> tuple[float, Action | None]:
    """
    Alpha-Beta search function.
    return (evaluation score, best action)
    """
    board_hash = current_board.current_hash
    alpha_original = alpha # save the original alpha value, for transposition table storage
    beta_original = beta # save the original beta value, for transposition table storage

    # 1. transposition table lookup
    cached_best_move = None
    if board_hash in transposition_table:
        entry = transposition_table[board_hash]
        tt_depth, tt_score, tt_flag, tt_best_move = entry
        cached_best_move = tt_best_move
        if tt_depth >= depth: # tt remaining depth is greater than or equal to the current depth, means the tt is search deeper than the current depth
            if tt_flag == EXACT: # exact value
                return tt_score, tt_best_move
            elif tt_flag == LOWERBOUND: # alpha/lowerbound
                alpha = max(alpha, tt_score)
            elif tt_flag == UPPERBOUND: # beta/upperbound
                beta = min(beta, tt_score)
            
            if alpha >= beta: # the updated alpha-beta boundary causes pruning
                return tt_score, tt_best_move

    # 2. reach the leaf node or specified depth
    if depth == 0 or current_board.is_game_over():
        return evaluate_board(current_board, eval_player_color), None

    best_move_for_this_node = None
    legal_moves = current_board.get_legal_moves(maximizing_player_color)
    
    # Move Ordering: Prioritize the cached best move from TT
    if cached_best_move and cached_best_move in legal_moves:
        legal_moves.remove(cached_best_move)
        legal_moves.insert(0, cached_best_move)

    if not legal_moves:
        # if there are no legal moves, it usually means the game is over or some special state
        return evaluate_board(current_board, eval_player_color), None

    # Initialize best_move_for_this_node with the first legal move if available
    # This ensures a move is returned even if all evaluations are equally bad.
    if legal_moves:
        best_move_for_this_node = legal_moves[0]

    if maximizing_player_color == eval_player_color: # the current node is a Max node
        max_eval = -math.inf
        for move in legal_moves:
            next_board = current_board.clone()
            next_board.apply_action(maximizing_player_color, move)
            
            # recursive call
            opponent_color = PlayerColor.RED if maximizing_player_color == PlayerColor.BLUE else PlayerColor.BLUE
            current_eval, _ = alpha_beta_search(next_board, depth - 1, alpha, beta, opponent_color, eval_player_color, transposition_table)
            
            if current_eval > max_eval:
                max_eval = current_eval
                best_move_for_this_node = move
            alpha = max(alpha, max_eval)
            if beta <= alpha:
                break # Beta pruning
        
        if board_hash not in transposition_table or depth >= transposition_table[board_hash][0]:
            # store to transposition table
            if max_eval <= alpha_original: # the real value <= max_eval (or <= alpha)
                flag_to_store = UPPERBOUND # upperbound
            elif max_eval >= beta_original: # the real value >= max_eval (or >= beta)
                flag_to_store = LOWERBOUND # lowerbound
            else:
                flag_to_store = EXACT # exact value
            transposition_table[board_hash] = (depth, max_eval, flag_to_store, best_move_for_this_node)
        
        return max_eval, best_move_for_this_node
    else: # the current node is a Min node
        min_eval = math.inf
        for move in legal_moves:
            next_board = current_board.clone()
            next_board.apply_action(maximizing_player_color, move)

            opponent_color = PlayerColor.RED if maximizing_player_color == PlayerColor.BLUE else PlayerColor.BLUE
            current_eval, _ = alpha_beta_search(next_board, depth - 1, alpha, beta, opponent_color, eval_player_color, transposition_table)

            if current_eval < min_eval:
                min_eval = current_eval
                best_move_for_this_node = move
            beta = min(beta, min_eval)
            if beta <= alpha:
                break # Alpha pruning
        
        if board_hash not in transposition_table or depth >= transposition_table[board_hash][0]:
            # store to transposition table
            if min_eval <= alpha_original:
                flag_to_store = UPPERBOUND
            elif min_eval >= beta_original:
                flag_to_store = LOWERBOUND
            else:
                flag_to_store = EXACT
            transposition_table[board_hash] = (depth, min_eval, flag_to_store, best_move_for_this_node)

        return min_eval, best_move_for_this_node