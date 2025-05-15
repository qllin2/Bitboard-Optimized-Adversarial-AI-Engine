# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Coord, Direction, \
    Action, MoveAction, GrowAction
from .bitboard import Bitboard

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
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """

        # get all legal moves
        legal_moves = self._board.get_legal_moves(self._color)
        
        # use simple strategy: if there is a move action, move, otherwise grow
        move_actions = [action for action in legal_moves if isinstance(action, MoveAction)]
        
        match self._color:
            case PlayerColor.RED:
                if move_actions:
                    selected_action = move_actions[0]  # select the first move action
                    print(f"Testing: RED is playing a MOVE action: {selected_action}")
                    return selected_action
                else:
                    print("Testing: RED is playing a GROW action")
                    return GrowAction()
            case PlayerColor.BLUE:
                if move_actions:
                    selected_action = move_actions[0]  # select the first move action
                    print(f"Testing: BLUE is playing a MOVE action: {selected_action}")
                    return selected_action
                else:
                    print("Testing: BLUE is playing a GROW action")
                    return GrowAction()

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

        # the following code is kept for debugging purposes
        match action:
            case MoveAction(coord, dirs):
                dirs_text = ", ".join([str(dir) for dir in dirs])
                print(f"Testing: {color} played MOVE action:")
                print(f"  Coord: {coord}")
                print(f"  Directions: {dirs_text}")
            case GrowAction():
                print(f"Testing: {color} played GROW action")
            case _:
                raise ValueError(f"Unknown action type: {action}")
        
        # print the current board state (optional, for debugging)
        # print("Current Board:")
        # print(self._board)
