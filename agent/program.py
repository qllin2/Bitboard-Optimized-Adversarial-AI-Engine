# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Coord, Direction, \
    Action, MoveAction, GrowAction
from .agent_core import Node, MCTS, GameState
from referee.game.exceptions import IllegalActionException

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
        self._board = None
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """

        # Below we have hardcoded two actions to be played depending on whether
        # the agent is playing as BLUE or RED. Obviously this won't work beyond
        # the initial moves of the game, so you should use some game playing
        # technique(s) to determine the best action to take.
        #match self._color:
         #   case PlayerColor.RED:
          #      print("Testing: RED is playing a MOVE action")
           #     return MoveAction(
            #        Coord(0, 3),
             #       [Direction.Down]
              #  )
            #case PlayerColor.BLUE:
             #   print("Testing: BLUE is playing a GROW action")
              #  return GrowAction()
        if self._board is None:
            from referee.game.board import Board
            self._board = Board()

        # 创建当前游戏状态
        current_state = GameState(last_move=None, board=self._board)

        # 使用MCTS算法选择最佳动作
        mcts = MCTS(current_state, iterations=50)
        best_action = mcts.search()

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
        """match action:
            case MoveAction(coord, dirs):
                dirs_text = ", ".join([str(dir) for dir in dirs])
                print(f"Testing: {color} played MOVE action:")
                print(f"  Coord: {coord}")
                print(f"  Directions: {dirs_text}")
            case GrowAction():
                print(f"Testing: {color} played GROW action")
            case _:
                raise ValueError(f"Unknown action type: {action}")"""
        # 更新内部棋盘状态
        if self._board is None:
            from referee.game.board import Board
            self._board = Board()

        try:
            self._board.apply_action(action)
        except IllegalActionException as e:
            print(f"Warning: Illegal action received in update: {e}")

        # 打印调试信息
        match action:
            case MoveAction(coord, dirs):
                dirs_text = ", ".join([str(dir) for dir in dirs])
                print(f"Testing: {color} played MOVE action")
                print(f"  Coord: {coord}")
                print(f"  Directions: {dirs_text}")
            case GrowAction():
                print(f"Testing: {color} played GROW action")
            case _:
                raise ValueError(f"Unknown action type: {action}")
