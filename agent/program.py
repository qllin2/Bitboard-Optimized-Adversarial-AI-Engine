# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Coord, Direction, \
    Action, MoveAction, GrowAction, constants
from .bitboard import Bitboard
from .alpha_beta_agent import alpha_beta_search 
import math
import time
import random

# define the search depth
SEARCH_DEPTH = 5 # you can adjust this value as needed
MAX_TURNS = constants.MAX_TURNS

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
        self._board = Bitboard(color)
        self._board.setup_initial_position()
        self._transposition_table = {}
        self._time_limit = referee["time_remaining"]
        self._space_remaining = referee["space_remaining"]
        self._space_limit = referee["space_limit"]

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
        
        # print(self._board)
        # call the alpha-beta search
        self._transposition_table.clear()
        remaining_turns = max(1, (MAX_TURNS - self._board.turns) / 2)
        time_budget = None
        time_remaining = referee["time_remaining"]
        if time_remaining is not None:
            time_budget = time_remaining / remaining_turns
            if self._board.turns < 5:
                time_budget *= 0.5
            elif self._board.turns >= 5 and self._board.turns < 10:
                time_budget *= 0.7
            elif self._board.turns >= 10 and self._board.turns < 20:
                time_budget *= 1.0
            elif self._board.turns >= 20 and self._board.turns < 40:
                time_budget *= 1.2
            elif self._board.turns >= 40:
                time_budget *= 1.5

            time_budget = min(time_budget, 5.0) # 5 seconds
            time_budget = max(time_budget, 0.5) # 0.5 seconds

        thinking_start_time = time.process_time()
        current_board = self._board.clone()
        best_action_overall = None
        best_eval_overall = -math.inf
        print(f"Agent {self._color}: Thinking time budget: {time_budget} seconds")
        print(f"Agent {self._color}: Current board turns: {current_board.turns}")
        print(f"Agent {self._color}: Thinking start time: {thinking_start_time}")
        print(f"Agent {self._color}: Time remaining: {time_remaining} seconds")

        for current_depth_limit in range(1, 10):
            if (time.process_time() - thinking_start_time) > time_budget:
                break

            print(f"Agent {self._color}: Thinking depth: {current_depth_limit}")

            # get the best action from the alpha-beta search
            current_depth_eval, current_depth_action = alpha_beta_search(
                current_board=current_board,
                depth=current_depth_limit,
                alpha=-math.inf,
                beta=math.inf,
                maximizing_player_color=self._color, # the current player
                eval_player_color=self._color,      # the player to evaluate
                transposition_table=self._transposition_table
            )

            if current_depth_eval > best_eval_overall:
                best_eval_overall = current_depth_eval
                best_action_overall = current_depth_action

            if best_eval_overall == math.inf:
                break
        
        if best_action_overall is None:
            final_legal_moves = current_board.get_legal_moves(self._color)
            if final_legal_moves:
                return random.choice(final_legal_moves)
            else:
                return None

        print(f"Agent {self._color}: My turn. Current board turns: {self._board.turns + 1}") 
        print(f"Agent {self._color}: Chosen action by Alpha-Beta: {best_action_overall} with eval score: {best_eval_overall}")
        return best_action_overall

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

        # the following print code can be kept for debugging
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
