from .bitboard import Bitboard, PIECE_LILYPAD
from referee.game import PlayerColor, Coord, Action
import math

# 简单的评估函数
# 红方 (RED) 的目标是 y=7 (第8行)
# 蓝方 (BLUE) 的目标是 y=0 (第1行)
RED_TARGET_ROW = 7
BLUE_TARGET_ROW = 0

def simple_evaluate(board: Bitboard, player_color: PlayerColor) -> float:
    """
    一个简单的评估函数。
    评估逻辑：(己方青蛙到目标底线的距离总和) - (对方青蛙到目标底线的距离总和)
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

    score -= board.count_pieces(PIECE_LILYPAD) * 0.05
    
    return score

# 置换表 (Transposition Table)
# 可以先用一个简单的字典实现
# 键是棋盘状态的哈希值，值可以是 (depth, score, flag, best_move)
# flag: 0 (精确值), 1 (alpha/下限), 2 (beta/上限)
transposition_table = {}

def alpha_beta_search(
    current_board: Bitboard, 
    depth: int, 
    alpha: float, 
    beta: float, 
    maximizing_player_color: PlayerColor, # 当前正在做决策的玩家 (轮到谁走)
    eval_player_color: PlayerColor       # 评估函数应从哪个玩家的视角进行评估
) -> tuple[float, Action | None]:
    """
    Alpha-Beta 搜索函数。
    返回 (评估分数, 最佳动作)
    """
    board_hash = current_board.current_hash
    alpha_original = alpha # 保存原始 alpha 值，用于置换表存储

    # 1. 置换表查询
    if board_hash in transposition_table:
        entry = transposition_table[board_hash]
        tt_depth, tt_score, tt_flag, tt_best_move = entry
        if tt_depth >= depth:
            if tt_flag == 0: # 精确值
                return tt_score, tt_best_move
            elif tt_flag == 1: # alpha/下限 (存储的是下限，所以可以用来提高 alpha)
                alpha = max(alpha, tt_score)
            elif tt_flag == 2: # beta/上限 (存储的是上限，所以可以用来降低 beta)
                beta = min(beta, tt_score)
            
            if alpha >= beta: # 如果更新后的alpha-beta边界导致剪枝
                return tt_score, tt_best_move

    # 2. 到达叶节点或指定深度
    if depth == 0 or current_board.is_game_over():
        return simple_evaluate(current_board, eval_player_color), None

    best_move_for_this_node = None
    legal_moves = current_board.get_legal_moves(maximizing_player_color)

    if not legal_moves:
        # 如果没有合法移动，通常意味着游戏结束或某种特殊状态
        # 此时也应该返回当前局面的评估值
        return simple_evaluate(current_board, eval_player_color), None

    if maximizing_player_color == eval_player_color: # 当前是 Max 节点
        max_eval = -math.inf
        for move in legal_moves:
            next_board = current_board.clone()
            next_board.apply_action(maximizing_player_color, move)
            
            # 递归调用，注意下一层的 maximizing_player_color 会改变
            opponent_color = PlayerColor.RED if maximizing_player_color == PlayerColor.BLUE else PlayerColor.BLUE
            current_eval, _ = alpha_beta_search(next_board, depth - 1, alpha, beta, opponent_color, eval_player_color)
            
            if current_eval > max_eval:
                max_eval = current_eval
                best_move_for_this_node = move
            alpha = max(alpha, current_eval)
            if beta <= alpha:
                break # Beta 剪枝
        
        # 存储到置换表
        flag_to_store = 0 # 默认为精确值
        if max_eval <= alpha_original: # 真实值 <= max_eval
            flag_to_store = 2 # 上限
        elif max_eval >= beta: # 真实值 >= max_eval (或者说 >= beta)
            flag_to_store = 1 # 下限
        transposition_table[board_hash] = (depth, max_eval, flag_to_store, best_move_for_this_node)
        
        return max_eval, best_move_for_this_node
    else: # 当前是 Min 节点
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
                break # Alpha 剪枝
        
        # 存储到置换表
        flag_to_store = 0 # 默认为精确值
        if min_eval >= beta: # 如果 min_eval 导致或可能导致其父Max节点剪枝(beta剪枝)
                               # 意味着该节点的真实值至少是 min_eval，因此 min_eval 是一个下限。
            flag_to_store = 1 # 下限 (LOWERBOUND)
        elif min_eval <= alpha_original: # 如果 min_eval <= alpha_original (父Max节点的alpha)
                                       # 意味着该节点的真实值至多是 min_eval，因此 min_eval 是一个上限。
            flag_to_store = 2 # 上限 (UPPERBOUND)
        transposition_table[board_hash] = (depth, min_eval, flag_to_store, best_move_for_this_node)

        return min_eval, best_move_for_this_node


# TODO: 实现置换表的存储逻辑

# TODO: 之后可以改进评估函数，例如考虑青蛙到目标线的距离