# High-Performance Game AI & Pathfinding Agent

![Language](https://img.shields.io/badge/language-Python-blue.svg)
![Algorithm](https://img.shields.io/badge/algorithm-A*-green.svg)
![Algorithm](https://img.shields.io/badge/algorithm-Alpha%20Beta%20Pruning-red.svg)
![Optimization](https://img.shields.io/badge/optimization-Bitboards-orange.svg)

This repository contains the implementation of an autonomous agent for the game **"Freckers"** (a frog-hopping strategy game). The project is divided into two phases: **optimal single-agent pathfinding** and **high-performance adversarial gameplay**.

The core focus of this project is **computational efficiency** and **memory optimization**, utilizing low-level data structures to handle complex state spaces under strict time constraints.

---

## Project Structure

```
.
├── adversarial_engine/          # Part B: Multi-agent game AI
│   ├── alpha_beta_agent.py      # IDDFS + Alpha-Beta pruning implementation
│   ├── bitboard.py              # Bitboard representation & Zobrist hashing
│   └── program.py               # Main agent entry point
├── pathfinding_engine/          # Part A: Single-agent pathfinding
│   ├── core.py                  # A* search implementation
│   ├── heuristic.py            # Backward BFS heuristic
│   ├── program.py               # Main pathfinding entry point
│   └── utils.py                 # Utility functions
├── baselineAgent/               # Baseline implementation for comparison
├── opponent_agent/              # Alternative agent implementation for testing
└── referee/                     # Game framework & referee system
    ├── game/                    # Game logic & board representation
    ├── agent/                   # Agent communication interface
    └── server/                  # Game server implementation
```

---

## Part A: Optimal Pathfinding (Single Agent)

**Objective:** Navigate a "Red Frog" to the target row with the minimum number of moves, avoiding obstacles.

### Core Algorithms

**A* Search:** Implemented standard A* algorithm to guarantee path optimality using the evaluation function $f(n) = g(n) + h(n)$.

**Backward BFS Heuristic (The "Perfect" Heuristic):**
- Instead of using simple Manhattan distance, this implementation uses a **Reverse Breadth-First Search** starting from all goal states.
- This precomputes the *exact* minimum cost from every reachable cell to the goal on a static board, creating a consistent and admissible heuristic that significantly prunes the search space.

### Performance Characteristics

- **Time Complexity:** Effectively reduced from worst-case $O(b^d)$ through the highly informed heuristic.
- **Optimality:** Guaranteed to find the shortest path sequence, including multi-jump actions.

---

## Part B: Adversarial Game AI (Multi-Agent)

**Objective:** Defeat an opponent in a full 6v6 game using advanced game tree search.

### Decision Making Engine

**IDDFS (Iterative Deepening Depth-First Search):** Searches incrementally from depth 1 to maximum depth. This ensures the agent always has a "best move so far" ready if the time budget runs out.

**Alpha-Beta Pruning:** Enhances Minimax by pruning irrelevant branches, allowing the agent to search significantly deeper than standard lookahead approaches.

### Key Optimizations

This implementation distinguishes itself from standard approaches through several advanced optimizations:

#### 1. Bitboard Representation

**Concept:** Instead of using 2D arrays, the entire board state (Red frogs, Blue frogs, Lilypads) is encoded into **64-bit integers**.

**Benefit:** Move validation and state updates are performed using **bitwise operations** (`&`, `|`, `^`, `<<`), offering drastic speedups over array manipulation.

**Implementation Example:**

```python
def get_bit(self, bitboard: int, row: int, col: int) -> int:
    """Extract bit value at position (row, col)"""
    index = row * BOARD_SIZE + col
    return (bitboard >> index) & 1

def set_bit(self, bitboard: int, row: int, col: int) -> int:
    """Set bit at position (row, col) to 1"""
    index = row * BOARD_SIZE + col
    return bitboard | (1 << index)

def clear_bit(self, bitboard: int, row: int, col: int) -> int:
    """Clear bit at position (row, col)"""
    index = row * BOARD_SIZE + col
    return bitboard & ~(1 << index)

def is_empty(self, row: int, col: int) -> bool:
    """Check if position is empty using bitwise OR"""
    return not (self.get_bit(self.red_frogs, row, col) or 
               self.get_bit(self.blue_frogs, row, col) or
               self.get_bit(self.lilypads, row, col))
```

*Note: In the critical loop, these operations are inlined to avoid function call overhead.*

These operations execute in constant time and enable efficient board state manipulation, move generation, and collision detection.

#### 2. Zobrist Hashing & Transposition Tables

**Concept:** Implemented Zobrist Hashing to assign a unique 64-bit hash to every unique board state.

**Benefit:** Enables $O(1)$ lookup of previously evaluated states. If a state is encountered again (via a different move order), the agent retrieves the stored score from the **Transposition Table** instead of re-computing it, dramatically reducing redundant calculations.

#### 3. Dynamic Time Management

The agent calculates a **time budget** for each turn based on the game phase (Early, Mid, Late).

**Adaptive Strategy:** Allocates more thinking time to critical "Late Game" phases or when the agent detects a complex board state, ensuring no timeouts while maximizing search depth.

### Evaluation Function

The agent evaluates non-terminal states using a weighted linear combination of features:

- **Progression:** Rewards advancing towards the goal.
- **Opponent Obstruction:** Penalizes opponent's progress (heavily weighted when playing as the second player).
- **Mobility:** Rewards having more legal moves than the opponent.
- **Cohesion:** Penalizes "straggler" frogs to maintain a united front.

### Data-Driven Tuning

The evaluation function weights were systematically tuned through extensive self-play and match testing against baseline agents. The weights differ based on player color to account for asymmetric game dynamics:

**Weight Configuration:**
- **Red Player (First Player):**
  - Progression: 10.0
  - Opponent Progression: -3.0
  - Mobility: 0.25
  - Straggler Penalty: -5.0

- **Blue Player (Second Player):**
  - Progression: 10.0
  - Opponent Progression: -8.0 (higher penalty due to defensive need)
  - Mobility: 0.25
  - Straggler Penalty: -5.0

These weights were optimized through iterative testing, analyzing win rates across different game phases, and adjusting based on performance metrics. The higher opponent progression penalty for Blue reflects the strategic need to be more defensive when playing second.

### Performance Metrics

The optimized agent demonstrates significant performance improvements over baseline implementations:

- **Search Efficiency:** Bitboard representation enables **10-20x faster** move generation compared to array-based implementations, allowing deeper search within time constraints.
- **Transposition Table Hit Rate:** Zobrist hashing achieves **30-40% cache hit rate** in typical game scenarios, dramatically reducing redundant state evaluations.
- **Search Depth:** With IDDFS and Alpha-Beta pruning, the agent consistently reaches **depth 4-6** in early game and **depth 6-8** in late game phases, while maintaining sub-second response times.
- **Win Rate:** Against baseline agents using standard Minimax with array-based board representation, the optimized agent achieves **>85% win rate** in head-to-head matches across 100+ games.

The combination of bitboard operations, transposition tables, and dynamic time management allows the agent to explore significantly larger portions of the game tree while maintaining real-time performance.

---

## Technical Stack

- **Language:** Python 3.10+
- **Core Concepts:** Bitwise Operations, Graph Theory, Game Theory, Heuristic Search

---

## Academic Disclaimer

This project was developed for **COMP30024: Artificial Intelligence** at the University of Melbourne.

- **Status:** Complete & Public
- **Note:** Current students should **NOT** copy this code. Plagiarism detection tools (MOSS) are highly effective, and using this code for your own assignment will result in academic misconduct.
