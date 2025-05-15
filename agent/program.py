# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Coord, Direction, \
    Action, MoveAction, GrowAction
from .bitboard import Bitboard
from .alpha_beta_agent import alpha_beta_search 
import math

# 定义搜索深度
SEARCH_DEPTH = 6 # 您可以根据需要调整这个值

class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Freckers game events.
    """

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self._color = color
        
        # initialize the board
        self._board = Bitboard()
        self._board.setup_initial_position()
        
        match color:
            case PlayerColor.RED:
                print(f"Agent: I am playing as RED. Search depth: {SEARCH_DEPTH}")
            case PlayerColor.BLUE:
                print(f"Agent: I am playing as BLUE. Search depth: {SEARCH_DEPTH}")

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """
        # 使用 self._board.turns 或者 self._board.ply_count 取决于您在bitboard.py中的实现
        print(f"Agent {self._color}: My turn. Current board turns: {self._board.turns}") 
        # print(self._board) # 打印当前棋盘状态 (可选)

        # 调用 Alpha-Beta 搜索
        eval_score, best_action = alpha_beta_search(
            current_board=self._board,
            depth=SEARCH_DEPTH,
            alpha=-math.inf,
            beta=math.inf,
            maximizing_player_color=self._color, # 当前轮到我方行动
            eval_player_color=self._color       # 评估函数从我方视角
        )
        print(f"Agent {self._color}: Chosen action by Alpha-Beta: {best_action} with eval score: {eval_score}")
        return best_action

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after a player has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        # There are two possible action types: MOVE and GROW. Below we check
        # which type of action was played and print out the details of the
        # action for demonstration purposes. You should replace this with your
        # own logic to update your agent's internal game state representation.
        
        # use Bitboard's apply_action method to update the board state
        self._board.apply_action(color, action)

        # 以下的打印代码可以保留用于调试
        # match action:
        #     case MoveAction(coord, dirs):
        #         dirs_text = ", ".join([str(dir) for dir in dirs])
        #         # print(f"Testing: {color} played MOVE action:")
        #         # print(f"  Coord: {coord}")
        #         # print(f"  Directions: {dirs_text}")
        #     case GrowAction():
        #         # print(f"Testing: {color} played GROW action")
        #     case _:
        #         # This case should ideally not be reached if action is always valid
        #         print(f"Agent {self._color}: Received unknown action type in update: {action}")
        
        # print("Current Board after update:")
        # print(self._board)
        # print(f"Board turns after update: {self._board.turns}")
