import random
import math
from collections import defaultdict
from referee.game.player import PlayerColor
from referee.game.coord import Direction
from referee.game.actions import MoveAction, GrowAction

# All 8 directions used for growth and movement
ALL_DIRECTIONS = [
    Direction.Up, Direction.UpRight, Direction.Right,
    Direction.DownRight, Direction.Down, Direction.DownLeft,
    Direction.Left, Direction.UpLeft
]

# Movement directions for RED and BLUE frogs
RED_DIRECTIONS = [
    Direction.Down, Direction.DownLeft, Direction.DownRight,
    Direction.Left, Direction.Right
]

BLUE_DIRECTIONS = [
    Direction.Up, Direction.UpLeft, Direction.UpRight,
    Direction.Left, Direction.Right
]

# Node class for MCTS tree structure
class Node:
    def __init__(self, state, parent=None, action=None, exploration_weight=1.0):
        self.state = state
        self.parent = parent
        self.action = action
        self.children: list[Node] = []
        self.visits = 0
        self.total_reward = [0.0, 0.0]
        self.exploration_weight = exploration_weight

        # Generate untried actions at initialization
        self.untried_actions = []
        legal_actions = state.get_legal_actions()
        for action_set in legal_actions.values():
            self.untried_actions.extend(action_set)

    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0

    def expand(self) -> "Node":
        # Expand node by applying an untried action
        action = self.untried_actions.pop()
        next_state = self.state.apply_action(action)
        child = Node(next_state, self, action, self.exploration_weight)
        self.children.append(child)
        return child

    def ucb_score(self, child: "Node") -> float:
        # UCB1 with custom bonus terms for progress, jumping, and goal proximity
        if child.visits == 0:
            return float('inf')
        idx = 0 if self.state.board.turn_color == PlayerColor.RED else 1
        exploit = child.total_reward[idx] / child.visits
        explore = self.exploration_weight * math.sqrt(
            math.log(self.visits) / child.visits
        )
        bonus = 0
        if isinstance(child.action, MoveAction):
            start = child.action.coord
            end = start
            path_len = len(child.action.directions)
            for direction in child.action.directions:
                end = GameState.plus_no_wrap(end, direction)
            if end:
                if self.state.board.turn_color == PlayerColor.RED:
                    progress = (end.r - start.r)
                    near_goal_bonus = 5 if end.r >= 6 else 0
                    jump_bonus = path_len * 0.5
                    bonus = (progress * 0.3) + near_goal_bonus + jump_bonus
                else:
                    progress = (start.r - end.r)
                    near_goal_bonus = 5 if end.r <= 1 else 0
                    jump_bonus = path_len * 0.5
                    bonus = (progress * 0.3) + near_goal_bonus + jump_bonus
        return exploit + explore + bonus

    def select_child(self) -> "Node":
        return max(self.children, key=lambda c: self.ucb_score(c))

    def update(self, reward: float):
        # Update reward and visit count with alternating perspective
        self.visits += 1
        if self.parent is None:
            self.total_reward[0] += reward
            self.total_reward[1] += (1 - reward)
        else:
            if self.state.board.turn_color == PlayerColor.RED:
                self.total_reward[0] += (1 - reward)
                self.total_reward[1] += reward
            else:
                self.total_reward[1] += (1 - reward)
                self.total_reward[0] += reward

# GameState represents current board state and legal actions
class GameState:
    def __init__(self, last_move, board):
        self.last_move = last_move
        self.board = board
        self.visited = set()
        self.actions = defaultdict(set)

    def get_legal_actions(self):
        # Generate all legal Move/Grow actions
        color = self.board.turn_color
        frogs = [coord for coord, cell_state in self.board._state.items()
                 if cell_state.state == color]
        for frog in frogs:
            if (color == PlayerColor.RED and frog.r == 7) or \
               (color == PlayerColor.BLUE and frog.r == 0):
                continue
            directions = RED_DIRECTIONS if color == PlayerColor.RED else BLUE_DIRECTIONS
            self.visited.clear()
            self.single_move(frog, directions)
            self.jump_move(frog, [], directions)
            self.grow_move(frog)
        return self.actions

    def single_move(self, coord, directions):
        # Add single-direction moves to action set
        for direction in directions:
            neighbor = self.plus_no_wrap(coord, direction)
            if neighbor and self.is_valid_coord(neighbor):
                try:
                    if self.board[neighbor].state == 'LilyPad':
                        action = MoveAction(coord, (direction,))
                        self.evaluate_action(action)
                except (IndexError, AttributeError):
                    continue

    def jump_move(self, current_pos, path, directions):
        # Recursively explore jump paths
        try:
            if self.board[current_pos].state != self.board.turn_color:
                return
        except (IndexError, AttributeError):
            return
        if path:
            action = MoveAction(current_pos, tuple(path.copy()))
            self.evaluate_action(action)
        for direction in directions:
            jump_over = self.plus_no_wrap(current_pos, direction)
            if not jump_over:
                continue
            landing = self.plus_no_wrap(jump_over, direction)
            if (landing and self.is_valid_coord(jump_over) and self.is_valid_coord(landing)):
                try:
                    if (self.board[jump_over].state in (PlayerColor.RED, PlayerColor.BLUE)
                        and self.board[landing].state == 'LilyPad'):
                        new_path = path + [direction]
                        if landing not in self.visited:
                            self.visited.add(landing)
                            self.jump_move(landing, new_path, directions)
                            self.visited.remove(landing)
                except (IndexError, AttributeError):
                    continue

    def grow_move(self, coord):
        # Add GrowAction if adjacent empty cell is found
        for direction in ALL_DIRECTIONS:
            neighbor = self.plus_no_wrap(coord, direction)
            if neighbor and self.is_valid_coord(neighbor):
                try:
                    if self.board[neighbor].state is None:
                        action = GrowAction()
                        self.evaluate_action(action)
                except (IndexError, AttributeError):
                    continue

    def evaluate_action(self, action):
        # Assign score to action based on progress and goal proximity
        score = 1
        if isinstance(action, MoveAction):
            start = action.coord
            end = action.coord
            path_len = len(action.directions)
            for direction in action.directions:
                end = self.plus_no_wrap(end, direction)
            if end:
                if self.board.turn_color == PlayerColor.RED:
                    progress = (end.r - start.r)
                    score = progress + path_len * 2 + 3
                    if end.r == 7:
                        score += 20
                elif self.board.turn_color == PlayerColor.BLUE:
                    progress = (start.r - end.r)
                    score = progress + path_len * 2 + 3
                    if end.r == 0:
                        score += 20
        elif isinstance(action, GrowAction):
            score = 0.1
        self.actions[score].add(action)

    @staticmethod
    def plus_no_wrap(coord, direction):
        # Safe coordinate addition without wrapping
        try:
            return coord + direction
        except ValueError:
            return None

    @staticmethod
    def is_valid_coord(coord):
        return 0 <= coord.r < 8 and 0 <= coord.c < 8

    def is_terminal(self):
        # Check game-end conditions: 6 frogs at goal or 150 turns
        red_goal = sum(1 for coord, cell_state in self.board._state.items()
                       if cell_state.state == PlayerColor.RED and coord.r == 7)
        blue_goal = sum(1 for coord, cell_state in self.board._state.items()
                        if cell_state.state == PlayerColor.BLUE and coord.r == 0)
        return red_goal >= 6 or blue_goal >= 6 or self.board.turn_count >= 150

    def apply_action(self, action):
        # Clone board and apply action
        from referee.game.board import Board
        new_board = Board(initial_state=self.board._state.copy(),
                          initial_player=self.board.turn_color)
        new_board.apply_action(action)
        return GameState(last_move=action, board=new_board)

    def evaluate(self, my_color):
        # Simple heuristic: reward frogs close to their goal
        my_score, opp_score = 0, 0
        for coord, cell_state in self.board._state.items():
            if my_color == PlayerColor.RED:
                if cell_state.state == PlayerColor.RED:
                    my_score += coord.r
                elif cell_state.state == PlayerColor.BLUE:
                    opp_score += (7 - coord.r)
            else:
                if cell_state.state == PlayerColor.BLUE:
                    my_score += (7 - coord.r)
                elif cell_state.state == PlayerColor.RED:
                    opp_score += coord.r
        return my_score - opp_score

# Depth-limited minimax for simulation or late-game precision
def minimax(state, depth, maximizing, my_color):
    if state.is_terminal() or depth == 0:
        return state.evaluate(my_color)
    actions = []
    for action_set in state.get_legal_actions().values():
        actions.extend(action_set)
    if not actions:
        return state.evaluate(my_color)
    if maximizing:
        value = float('-inf')
        for action in actions:
            value = max(value, minimax(state.apply_action(action), depth - 1, False, my_color))
        return value
    else:
        value = float('inf')
        for action in actions:
            value = min(value, minimax(state.apply_action(action), depth - 1, True, my_color))
        return value

# MCTS controller class
class MCTS:
    def __init__(self, state, iterations=1000, simulation_depth=50):
        self.root = Node(state)
        self.iterations = iterations
        self.simulation_depth = simulation_depth

    def search(self):
        for _ in range(self.iterations):
            node = self.select()
            reward = self.simulate(node)
            self.backpropagate(node, reward)
        best_child = max(self.root.children, key=lambda c: c.visits, default=None)
        return best_child.state.last_move if best_child else GrowAction()

    def select(self):
        current = self.root
        while not current.state.is_terminal():
            if current.untried_actions:
                return current.expand()
            current = current.select_child()
        return current

    def simulate(self, node):
        # Mixed simulation: random rollout + minimax for deeper levels
        state = node.state
        depth = 0
        while not state.is_terminal() and depth < self.simulation_depth:
            if depth >= 30:
                eval_score = minimax(state, 2, True, self.root.state.board.turn_color)
                return min(1.0, max(0.0, (eval_score + 50) / 100))
            legal_actions = []
            for action_set in state.get_legal_actions().values():
                legal_actions.extend(action_set)
            if not legal_actions:
                break
            state = state.apply_action(random.choice(legal_actions))
            depth += 1
        eval_score = state.evaluate(self.root.state.board.turn_color)
        return min(1.0, max(0.0, (eval_score + 50) / 100))

    def backpropagate(self, node, reward):
        while node:
            node.update(reward)
            node = node.parent
            reward = 1 - reward  # Alternate perspective on reward




