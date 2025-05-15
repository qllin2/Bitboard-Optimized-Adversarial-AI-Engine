# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part B: Game Playing Agent - Bitboard测试

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.bitboard import Bitboard, PIECE_RED, PIECE_BLUE, PIECE_LILYPAD, BOARD_SIZE
from referee.game import PlayerColor, Coord, Direction, MoveAction, GrowAction

def print_board_details(board):
    """打印棋盘的详细状态，包括每个位置的内容"""
    print("棋盘详细状态:")
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board.get_piece(r, c)
            if piece == PIECE_RED:
                print(f"位置({r},{c}): 红蛙")
            elif piece == PIECE_BLUE:
                print(f"位置({r},{c}): 蓝蛙")
            elif piece == PIECE_LILYPAD:
                print(f"位置({r},{c}): 荷叶")

def test_initialization():
    """测试Bitboard初始化"""
    board = Bitboard()
    board.setup_initial_position()
    
    # 打印各类棋子数量
    red_count = board.count_pieces(PIECE_RED)
    blue_count = board.count_pieces(PIECE_BLUE)
    lilypad_count = board.count_pieces(PIECE_LILYPAD)
    print(f"红蛙数量: {red_count}")
    print(f"蓝蛙数量: {blue_count}")
    print(f"荷叶数量: {lilypad_count}")
    
    # 验证初始红蛙数量为6
    assert board.count_pieces(PIECE_RED) == 6
    
    # 验证初始蓝蛙数量为6
    assert board.count_pieces(PIECE_BLUE) == 6
    
    # 初始荷叶数量为16
    assert board.count_pieces(PIECE_LILYPAD) == 16
    
    # 打印初始棋盘
    print("初始棋盘:")
    print(board)
    
    # 打印详细状态
    print_board_details(board)

def test_move_actions():
    """测试移动操作"""
    board = Bitboard()
    board.setup_initial_position()
    
    print("移动前棋盘:")
    print(board)
    print_board_details(board)
    
    # 测试简单移动
    # 找到一个红蛙，以及其旁边的一个荷叶进行移动测试
    src_r, src_c, target_r, target_c, move_direction = -1,-1,-1,-1,None
    found_simple_move = False
    for r_frog in range(BOARD_SIZE):
        for c_frog in range(BOARD_SIZE):
            if board.get_piece(r_frog, c_frog) == PIECE_RED:
                # 检查红蛙允许的移动方向
                allowed_directions = [Direction.Down, Direction.DownLeft, Direction.DownRight, Direction.Left, Direction.Right]
                for direction_option in allowed_directions:
                    dr, dc = board._direction_to_offset(direction_option)
                    tr, tc = r_frog + dr, c_frog + dc
                    if 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE and board.has_lilypad(tr, tc):
                        src_r, src_c = r_frog, c_frog
                        target_r, target_c = tr, tc
                        move_direction = direction_option
                        found_simple_move = True
                        break
                if found_simple_move: break
        if found_simple_move: break
    
    if not found_simple_move:
        print("无法找到合适的简单移动测试位置，跳过简单移动测试")
    else:
        print(f"测试简单移动: 红蛙从({src_r},{src_c}) 移动到荷叶 ({target_r},{target_c}) 使用方向 {move_direction}")
        action = MoveAction(Coord(src_r, src_c), [move_direction])
        result = board.apply_action(PlayerColor.RED, action)
        print(f"简单移动操作返回值: {result}")
        assert result is True
        
        print("简单移动后棋盘:")
        print(board)
        print_board_details(board)
        
        old_piece = board.get_piece(src_r, src_c)
        new_piece = board.get_piece(target_r, target_c)
        print(f"原位置({src_r},{src_c})棋子: {old_piece}")
        print(f"新位置({target_r},{target_c})棋子: {new_piece}")
        
        assert old_piece is None
        assert new_piece == PIECE_RED
        print("简单移动验证通过!")

    # 测试跳跃
    # 基于初始棋盘重新设置，或确保棋盘状态适合测试跳跃
    board.setup_initial_position() # 重置棋盘以获得可预测的跳跃场景
    print("\n进行跳跃测试，重置棋盘到初始状态:")
    print(board)

    # 寻找一个红蛙，它前方有一个可跳过的棋子（任一颜色），且落点是一个荷叶
    jump_src_r, jump_src_c = -1, -1
    jump_mid_r, jump_mid_c = -1, -1 # 跳过的棋子
    jump_target_r, jump_target_c = -1, -1 # 落点荷叶
    jump_direction = None
    found_jump_scenario = False

    for r_frog in range(BOARD_SIZE):
        for c_frog in range(BOARD_SIZE):
            if board.get_piece(r_frog, c_frog) == PIECE_RED:
                # 红蛙允许的移动/跳跃方向
                allowed_directions = [Direction.Down, Direction.DownLeft, Direction.DownRight, Direction.Left, Direction.Right]
                for direction_option in allowed_directions:
                    dr, dc = board._direction_to_offset(direction_option)
                    
                    r_mid, c_mid = r_frog + dr, c_frog + dc # 被跳过的棋子位置
                    r_land, c_land = r_frog + 2*dr, c_frog + 2*dc # 落点位置

                    if (0 <= r_mid < BOARD_SIZE and 0 <= c_mid < BOARD_SIZE and
                        0 <= r_land < BOARD_SIZE and 0 <= c_land < BOARD_SIZE):
                        # 被跳过的位置必须有棋子 (红或蓝)
                        if board.get_piece(r_mid, c_mid) in [PIECE_RED, PIECE_BLUE]:
                            # 落点必须是荷叶
                            if board.has_lilypad(r_land, c_land):
                                jump_src_r, jump_src_c = r_frog, c_frog
                                jump_mid_r, jump_mid_c = r_mid, c_mid
                                jump_target_r, jump_target_c = r_land, c_land
                                jump_direction = direction_option
                                found_jump_scenario = True
                                break
                if found_jump_scenario: break
        if found_jump_scenario: break
    
    if not found_jump_scenario:
        print("在初始棋盘上未找到合适的红方跳跃场景，尝试手动设置一个场景")
        # 手动设置一个跳跃场景: R at (0,1), B at (1,1), L at (2,1) -> R jumps to (2,1)
        board.setup_initial_position() # 确保干净的棋盘
        board.set_piece(0,1, PIECE_RED)
        board.set_piece(1,1, PIECE_BLUE) # 或者 PIECE_RED
        board.set_piece(2,1, PIECE_LILYPAD)
        jump_src_r, jump_src_c = 0, 1
        jump_mid_r, jump_mid_c = 1, 1
        jump_target_r, jump_target_c = 2, 1
        jump_direction = Direction.Down
        print(f"手动设置跳跃场景: 红蛙({jump_src_r},{jump_src_c}) 跳过 ({jump_mid_r},{jump_mid_c}) 到达荷叶 ({jump_target_r},{jump_target_c})")
        print("设置后棋盘:")
        print(board)

    piece_over_jumped = board.get_piece(jump_mid_r, jump_mid_c) # 记录被跳过棋子的原始类型

    # 执行跳跃 (跳跃动作在 apply_action 中通常表示为单个方向，由apply_action判断是跳跃还是移动)
    # 或者，如果get_legal_moves会返回多段跳跃，这里的测试用例可能需要调整
    # 根据当前的 apply_action 逻辑, 如果 directions 长度为1，它会自行判断是移动还是跳跃
    # 但为了显式测试跳跃，我们应该确保它被识别为跳跃，或者使用get_legal_moves生成的跳跃动作
    # 这里我们假设要测试的是 apply_action 对单次跳跃的解析

    # 为了让 apply_action 识别为跳跃而不是单步，目标位置(jump_mid_r, jump_mid_c)不能是荷叶
    # 且 (jump_mid_r, jump_mid_c) 上有棋子, (jump_target_r, jump_target_c) 是荷叶
    # 这个条件已在寻找场景时满足

    action = MoveAction(Coord(jump_src_r, jump_src_c), [jump_direction]) # 单个方向，apply_action会判断
    result = board.apply_action(PlayerColor.RED, action)
    print(f"跳跃操作返回值: {result}")
    assert result is True

    print("跳跃后棋盘:")
    print(board)
    print_board_details(board)

    old_piece = board.get_piece(jump_src_r, jump_src_c)
    middle_piece_after_jump = board.get_piece(jump_mid_r, jump_mid_c)
    new_piece = board.get_piece(jump_target_r, jump_target_c)
    
    print(f"原位置({jump_src_r},{jump_src_c})棋子: {old_piece}")
    print(f"中间位置({jump_mid_r},{jump_mid_c})棋子 (跳跃后): {middle_piece_after_jump}")
    print(f"新位置({jump_target_r},{jump_target_c})棋子: {new_piece}")

    assert old_piece is None  # 原位置没有棋子
    assert middle_piece_after_jump == piece_over_jumped # 中间位置棋子不变
    assert new_piece == PIECE_RED  # 新位置有红蛙
    
    print("跳跃验证通过!")

def test_grow_action():
    """测试GROW操作"""
    board = Bitboard()
    board.setup_initial_position()
    initial_lilypad_count = board.count_pieces(PIECE_LILYPAD)
    print(f"GROW前荷叶数量: {initial_lilypad_count}")

    # 执行GROW动作 (假设为红方)
    result = board.apply_action(PlayerColor.RED, GrowAction())
    assert result is True # GrowAction应该总是成功除非游戏结束等特殊情况

    lilypad_count_after_grow = board.count_pieces(PIECE_LILYPAD)
    print(f"GROW后荷叶数量: {lilypad_count_after_grow}")
    # 断言荷叶数量有所增加，或者至少没有减少（如果所有潜在位置都已是荷叶或被占据）
    # 一个更强的断言是，如果存在可生长的空位，则数量必定增加
    # 这里我们简单检查是否大于等于初始数量，理想情况是检查是否至少有一个潜在荷叶成功生长
    assert lilypad_count_after_grow >= initial_lilypad_count 
    # 我们不再检查 potential_lilypads，因为 Bitboard 类中没有这个属性。
    # 更详细的生长测试在 test_complex_mid_game_scenarios 中。
    # if board.red_potential_lilypads != 0: # 如果之前有潜在位置
    #      assert lilypad_count_after_grow > initial_lilypad_count # 则数量应该增加

    print("GROW后棋盘:")
    print(board)

    # 测试吃掉荷叶（即青蛙移动到荷叶上）
    # 先确保棋盘上有荷叶和青蛙
    board.setup_initial_position() # 重置以获得可预测状态
    board.apply_action(PlayerColor.RED, GrowAction()) # 生长一些荷叶
    print("\n测试吃掉荷叶，棋盘状态:")
    print(board)
    
    lilypad_pos_to_eat = None
    frog_to_move_src = None
    move_to_eat_direction = None

    # 找到一个红蛙及其可移动到的相邻荷叶
    found_eat_scenario = False
    for r_frog in range(BOARD_SIZE):
        for c_frog in range(BOARD_SIZE):
            if board.get_piece(r_frog, c_frog) == PIECE_RED:
                allowed_directions = [Direction.Down, Direction.DownLeft, Direction.DownRight, Direction.Left, Direction.Right]
                for direction_option in allowed_directions:
                    dr, dc = board._direction_to_offset(direction_option)
                    tr, tc = r_frog + dr, c_frog + dc
                    if 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE and board.has_lilypad(tr, tc):
                        frog_to_move_src = Coord(r_frog, c_frog)
                        lilypad_pos_to_eat = Coord(tr, tc)
                        move_to_eat_direction = direction_option
                        found_eat_scenario = True
                        break
                if found_eat_scenario: break
        if found_eat_scenario: break
    
    if found_eat_scenario:
        print(f"找到吃荷叶场景: 红蛙从{frog_to_move_src} 移动到荷叶 {lilypad_pos_to_eat}")
        action = MoveAction(frog_to_move_src, [move_to_eat_direction])
        board.apply_action(PlayerColor.RED, action)
        
        print("吃掉荷叶后棋盘:")
        print(board)
        assert not board.has_lilypad(lilypad_pos_to_eat.r, lilypad_pos_to_eat.c) # 荷叶没了
        assert board.get_piece(lilypad_pos_to_eat.r, lilypad_pos_to_eat.c) == PIECE_RED # 蛙在原荷叶位置
        print("吃掉荷叶验证通过!")
    else:
        print("未找到合适的吃荷叶场景进行测试。")

def test_zobrist_hashing():
    """测试Zobrist哈希的一致性"""
    board1 = Bitboard()
    board1.setup_initial_position()

    initial_hash = board1.current_hash

    board2 = board1.clone()
    assert board1.current_hash == board2.current_hash, "克隆棋盘的哈希值应相同"
    print("克隆棋盘哈希值相同！")

    # 测试set_piece和清除piece对哈希的影响
    print("\n测试 set_piece / clear_piece 对Zobrist哈希的影响...")
    board1.set_piece(4, 4, PIECE_LILYPAD) # 在 (4,4) 放置荷叶
    hash_after_set_lilypad = board1.current_hash
    assert hash_after_set_lilypad != initial_hash, "放置荷叶后哈希值应改变"
    print(f"放置荷叶于(4,4)后哈希: {hash_after_set_lilypad}")

    board1.set_piece(4, 4, None) # 清除 (4,4) 的荷叶
    hash_after_clear_lilypad = board1.current_hash
    assert hash_after_clear_lilypad == initial_hash, "清除荷叶后哈希值应恢复到初始状态（如果棋盘回到该状态）"
    print(f"清除(4,4)荷叶后哈希: {hash_after_clear_lilypad} (期望: {initial_hash})")
    print("Set/Clear piece 哈希测试通过!")

    # 测试移动操作对哈希的影响
    print("\n测试移动操作对Zobrist哈希的影响...")
    board_move_test = Bitboard()
    # 创建一个简单可控的局面
    # R . L
    # . . .
    # . . .
    board_move_test.set_piece(0, 0, PIECE_RED)
    board_move_test.set_piece(0, 2, PIECE_LILYPAD)
    # 记录这个特定棋盘状态的哈希 (R at (0,0), L at (0,2), बाकी सब खाली)
    # (0,1) 应该是空的，以便红蛙可以移动或跳跃到 (0,2)
    board_move_test.set_piece(0, 1, None) # 确保中间是空的
    
    initial_move_test_hash = board_move_test.current_hash
    print(f"移动测试初始棋盘 (R at (0,0), L at (0,2)):")
    print(board_move_test)
    print(f"初始哈希: {initial_move_test_hash}")

    # 准备移动: 红蛙从 (0,0) 到 (0,2) (假设是跳跃或有效移动)
    # 如果是单步移动，(0,1)必须是荷叶。这里我们测试跳跃或通过(0,1)的移动。
    # 为了简单，我们假设 (0,1) 是空的，(0,2) 是荷叶，看能否单步移动到(0,2)
    # 红方只能 L, R, D, DL, DR. 从 (0,0) 到 (0,2) 是两个 Right.
    # 这需要 (0,1) 是可跳过的棋子，(0,2) 是荷叶。
    # 或者，如果规则允许直接移动两格到荷叶上（不常见）
    # 让我们设置一个更清晰的单步移动场景
    board_move_test = Bitboard() # Reset
    board_move_test.set_piece(1, 1, PIECE_RED)      # 红蛙在 (1,1)
    board_move_test.set_piece(1, 2, PIECE_LILYPAD)  # 荷叶在 (1,2)
    # (1,1) R, (1,2) L
    
    state_before_move_str = str(board_move_test)
    red_frogs_before, blue_frogs_before, lilypads_before = board_move_test.red_frogs, board_move_test.blue_frogs, board_move_test.lilypads
    hash_before_move = board_move_test.current_hash
    print(f"移动测试棋盘 (R at (1,1), L at (1,2)):")
    print(board_move_test)
    print(f"移动前哈希: {hash_before_move}")

    # 执行移动: 红蛙从 (1,1) 到 (1,2) (Direction.Right)
    action = MoveAction(Coord(1,1), [Direction.Right])
    result = board_move_test.apply_action(PlayerColor.RED, action)
    assert result is True, "移动操作应成功"

    hash_after_move = board_move_test.current_hash
    print("移动后棋盘 (R at (1,2), (1,1) is None):")
    print(board_move_test)
    print(f"移动后哈希: {hash_after_move}")
    assert hash_before_move != hash_after_move, "有效移动后哈希值应改变"

    # 手动将棋盘恢复到移动前的状态，验证哈希值是否也恢复
    # 移动前: (1,1) R, (1,2) L
    # 移动后: (1,1) None, (1,2) R
    # 恢复操作：
    # 1. 将 (1,2) 从 R 变回 L
    # 2. 将 (1,1) 从 None 变回 R
    board_move_test.set_piece(1, 2, PIECE_LILYPAD) # 恢复 (1,2) 为荷叶
    board_move_test.set_piece(1, 1, PIECE_RED)     # 恢复 (1,1) 为红蛙
    
    assert board_move_test.red_frogs == red_frogs_before
    assert board_move_test.blue_frogs == blue_frogs_before
    assert board_move_test.lilypads == lilypads_before
    # assert str(board_move_test) == state_before_move_str # 字符串表示也应相同

    hash_after_manual_revert = board_move_test.current_hash
    print("手动恢复到移动前状态后的棋盘:")
    print(board_move_test)
    print(f"手动恢复后哈希: {hash_after_manual_revert}")
    
    assert hash_after_manual_revert == hash_before_move, "手动恢复棋盘状态后，哈希值应回到移动前的值"
    print("移动操作的Zobrist哈希测试（移动和手动恢复）通过!")
    print("Zobrist哈希测试全部通过!")

def test_legal_moves():
    """测试合法移动生成"""
    board = Bitboard()
    board.setup_initial_position()
    
    # 获取所有合法移动
    red_moves = board.get_legal_moves(PlayerColor.RED)
    blue_moves = board.get_legal_moves(PlayerColor.BLUE)
    
    print(f"红方合法移动数量: {len(red_moves)}")
    print(f"蓝方合法移动数量: {len(blue_moves)}")
    
    # 至少应该有一个GROW动作和一些移动动作
    assert len(red_moves) > 1
    assert len(blue_moves) > 1
    
    # 打印一些移动示例
    print("红方移动示例:")
    for i, move in enumerate(red_moves[:5]):
        print(f"  {i+1}: {move}")
    if not any(isinstance(m, MoveAction) for m in red_moves):
        print("警告: 红方没有生成任何MoveAction!")
    if not any(isinstance(m, GrowAction) for m in red_moves):
        print("警告: 红方没有生成GrowAction!")

    print("蓝方移动示例:")
    for i, move in enumerate(blue_moves[:5]):
        print(f"  {i+1}: {move}")
    if not any(isinstance(m, MoveAction) for m in blue_moves):
        print("警告: 蓝方没有生成任何MoveAction!")
    if not any(isinstance(m, GrowAction) for m in blue_moves):
        print("警告: 蓝方没有生成GrowAction!")

def test_complex_mid_game_scenarios():
    """测试复杂中局场景，特别是连续跳跃和荷叶生长"""
    print("\n" + "="*50 + "\n")
    print("开始测试复杂中局场景...")
    board = Bitboard()

    # 场景1: 测试连续跳跃
    # R . B . L
    # . . . . .
    # L . R . L
    # . . . . .
    # . . L . .
    print("\n--- 测试连续跳跃 ---")
    board.set_piece(0, 0, PIECE_RED)    # 跳跃蛙
    board.set_piece(0, 2, PIECE_BLUE)   # 第一个被跳过的
    board.set_piece(0, 4, PIECE_LILYPAD) # 第一个落点
    board.set_piece(2, 0, PIECE_LILYPAD) # 中间某个荷叶 (无关)
    board.set_piece(2, 2, PIECE_RED)    # 第二个被跳过的
    board.set_piece(2, 4, PIECE_LILYPAD) # 第二个落点
    board.set_piece(4, 2, PIECE_LILYPAD) # 第三个落点

    print("连续跳跃测试棋盘设置:")
    print(board)
    # 预期: 红蛙 (0,0) 可以跳到 (0,4) [D.Right, D.Right]
    # 然后从 (0,4) 可以跳到 (2,2) [D.DownLeft, D.DownLeft] (跳过(1,3)假设为空, (2,2)是红蛙, 不对, (2,2)必须是lilypad才能落)
    # 重设场景，确保落点是荷叶，被跳的是棋子
    board = Bitboard() # 清空
    # R1 at (0,0)
    # B1 at (0,1) to be jumped
    # L1 at (0,2) first landing
    # R2 at (1,2) to be jumped (frog can jump any color)
    # L2 at (2,2) second landing
    board.set_piece(0, 0, PIECE_RED)    # R1
    board.set_piece(0, 1, PIECE_BLUE)   # B1
    board.set_piece(0, 2, PIECE_LILYPAD)# L1
    board.set_piece(1, 2, PIECE_RED)    # R2 (could be blue too)
    board.set_piece(2, 2, PIECE_LILYPAD)# L2

    print("修正后的连续跳跃测试棋盘设置:")
    print(board)
    print(f"红蛙坐标: {board.red_frog_coords}")
    print(f"蓝蛙坐标: {board.blue_frog_coords}")

    legal_moves_red = board.get_legal_moves(PlayerColor.RED)
    print("红方合法移动:")
    found_double_jump = False
    expected_double_jump_path = [Direction.Right, Direction.Down]
    # (0,0) -> Right (jumps (0,1)) -> lands (0,2)
    # (0,2) -> Down  (jumps (1,2)) -> lands (2,2)

    for move in legal_moves_red:
        if isinstance(move, MoveAction) and move.coord == Coord(0,0) and len(move.directions) == 2:
            print(f"  找到潜在双段跳跃: {move}")
            if move.directions[0] == Direction.Right and move.directions[1] == Direction.Down:
                 found_double_jump = True
                 print(f"    找到预期的连续跳跃路径: {move.directions}")
                 # 应用此动作
                 board_after_jump = board.clone()
                 result = board_after_jump.apply_action(PlayerColor.RED, move)
                 assert result is True
                 print("    应用连续跳跃后棋盘:")
                 print(board_after_jump)
                 assert board_after_jump.get_piece(0,0) is None # 原位置为空
                 assert board_after_jump.get_piece(0,1) == PIECE_BLUE # 被跳过的B1还在
                 assert board_after_jump.get_piece(1,2) == PIECE_RED # 被跳过的R2还在
                 # 第一个落点(0,2)在执行整个连续跳跃动作 MoveAction(Coord(0,0), [Right, Down]) 后应仍为荷叶，
                 # 因为apply_action会将棋子从(0,0)直接移动到最终目的地(2,2)。
                 # (0,2)作为路径上的荷叶是必须的，但它本身不被此单一复合动作消耗。
                 assert board_after_jump.get_piece(0,2) == PIECE_LILYPAD
                 assert board_after_jump.get_piece(2,2) == PIECE_RED # 最终落点是红蛙
                 break 
    assert found_double_jump, "未能找到预期的连续跳跃"
    print("连续跳跃测试通过!")

    # 场景2: 测试荷叶生长在中局
    print("\n--- 测试中局荷叶生长 ---")
    board = Bitboard() # 清空
    # . R .
    # . . B
    # . . .
    board.set_piece(0, 1, PIECE_RED)  # 红蛙
    board.set_piece(1, 2, PIECE_BLUE) # 蓝蛙
    print("荷叶生长测试棋盘设置 (无荷叶初识):")
    print(board)
    initial_lilypads = board.count_pieces(PIECE_LILYPAD)
    assert initial_lilypads == 0

    # 红方生长
    print("执行红方GROW...")
    board.apply_action(PlayerColor.RED, GrowAction())
    print("红方GROW后棋盘:")
    print(board)
    lilypads_after_red_grow = board.count_pieces(PIECE_LILYPAD)
    # 红蛙(0,1)周围的空位: (0,0), (0,2), (1,0), (1,1)
    # (1,1) 应该生长. (1,0) 应该生长. (0,0) 应该生长. (0,2) 应该生长.
    # (1,2)是蓝蛙，不生长. 共4个
    assert lilypads_after_red_grow == 4, f"预期红方生长后有4个荷叶，实际为{lilypads_after_red_grow}"
    assert board.has_lilypad(0,0) and board.has_lilypad(0,2) and board.has_lilypad(1,0) and board.has_lilypad(1,1)

    # 蓝方生长 (在红方生长之后)
    print("执行蓝方GROW...")
    board.apply_action(PlayerColor.BLUE, GrowAction())
    print("蓝方GROW后棋盘:")
    print(board)
    lilypads_after_blue_grow = board.count_pieces(PIECE_LILYPAD)
    # 蓝蛙(1,2)周围的空位 (之前红方已填补了一些):
    # (0,2) 已是荷叶.
    # (1,1) 已是荷叶.
    # (2,1) 空, (2,2) 空, (2,3) 空 (如果边界内).
    # (0,3) 空 (边界内), (1,3) 空 (边界内)
    # 预期额外生长在 (2,1), (2,2), (2,3), (0,3), (1,3) (假设BOARD_SIZE足够大，这里是8x8)
    # 8x8, (2,3) valid, (0,3) valid, (1,3) valid
    # 蓝蛙(1,2)能新生成的荷叶：(2,1), (2,2) (因为(0,2) (1,1) (0,1)R (0,0)L (1,0)L (2,0)空)
    # (0,1)R (0,2)L (1,1)L (1,2)B (1,0)L (0,0)L 
    # Blue at (1,2). Neighbors: (0,1)R, (0,2)L, (0,3)Empty, (1,1)L, (1,3)Empty, (2,1)Empty, (2,2)Empty, (2,3)Empty
    # New lilypads for blue: (0,3), (1,3), (2,1), (2,2), (2,3) -> 5个
    # Total lilypads = 4 (from red) + 5 (from blue) = 9
    assert lilypads_after_blue_grow == 4 + 5, f"预期红蓝双方生长后有9个荷叶，实际为{lilypads_after_blue_grow}"
    assert board.has_lilypad(0,3) and board.has_lilypad(1,3) and board.has_lilypad(2,1) and board.has_lilypad(2,2) and board.has_lilypad(2,3)
    print("中局荷叶生长测试通过!")

    print("\n复杂中局场景测试完成!")

# 主测试执行部分
if __name__ == "__main__":
    print("开始测试Bitboard实现...")
    test_initialization()
    print("\n" + "="*50 + "\n")
    
    test_move_actions() # 这个测试可能需要调整，因为之前的找空位逻辑可能不太适用复杂跳跃
    print("\n" + "="*50 + "\n")
    
    test_grow_action() # 这个测试主要是基于初始布局的，可以保留
    print("\n" + "="*50 + "\n")
    
    test_zobrist_hashing()
    print("\n" + "="*50 + "\n")
    
    test_legal_moves() # 这个测试主要是检查有无移动和数量，可以保留
    print("\n" + "="*50 + "\n")

    test_complex_mid_game_scenarios() # 新增的复杂场景测试
    
    print("所有测试完成!") 