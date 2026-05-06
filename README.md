# Chess

A two-player chess game built with Python and Pygame. Play against an AI opponent or use it as a local two-player board.

## Features

- Full chess rules — castling, en passant, pawn promotion, check/checkmate/stalemate detection
- AI opponent using Negamax with alpha-beta pruning
- Opening book covering major openings (Sicilian, Ruy Lopez, King's Indian, French, etc.)
- Move animation
- Undo moves with `Z`
- Highlighted valid moves on piece selection

## Requirements

- Python 3.x
- Pygame

```
pip install pygame
```

## Running

```
python ChessMain.py
```

## Project Structure

```
├── ChessMain.py       # Game loop, rendering, input handling
├── ChessEngine.py     # Board state, move generation, game rules
├── ChessAI.py         # AI logic, evaluation, opening book
└── pieces/            # PNG images for each piece
```

## Controls

| Key / Action | Description |
|---|---|
| Click a piece | Select it, highlights valid moves |
| Click a destination | Move the piece |
| `Z` | Undo last two moves (yours + AI's) |
| `R` | Reset the board |

## AI

The AI runs on a separate thread to keep the UI responsive. It uses:

- **Negamax with alpha-beta pruning** — searches up to depth 3
- **Iterative deepening** — builds move ordering across depths
- **Quiescence search** — extends search on captures to avoid horizon effect
- **Null move pruning** — skips a turn to detect beta cutoffs early
- **Transposition table** — caches previously evaluated positions
- **Killer move heuristic** — prioritizes moves that caused cutoffs at the same depth
- **Opening book** — hardcoded responses for the first several moves of common openings

## Configuration

In `ChessAI.py`:

```python
DEPTH = 3  # Search depth — higher = stronger but slower
```

In `ChessMain.py`:

```python
player_white = True   # True = human plays white
player_black = False  # True = human plays black
```

Set both to `True` for local two-player. Set both to `False` to watch AI vs AI.
