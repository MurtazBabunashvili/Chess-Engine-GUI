import sys
import ChessEngine
import ChessAI


def uci_loop():
    gs = ChessEngine.GameState()

    while True:
        line = input().strip()

        if line == "uci":
            print("id name MyChessEngine")
            print("id author You")
            print("uciok")

        elif line == "isready":
            print("readyok")

        elif line == "ucinewgame":
            gs = ChessEngine.GameState()
            ChessAI.transposition_table = ChessAI.TranspositionTable()

        elif line.startswith("position"):
            gs = ChessEngine.GameState()
            parts = line.split()

            if "moves" in parts:
                moves_start = parts.index("moves") + 1
                move_strings = parts[moves_start:]
                for move_str in move_strings:
                    valid_moves = gs.get_valid_moves()
                    for move in valid_moves:
                        if move.getChessNotation() == move_str:
                            gs.make_move(move)
                            break

        elif line.startswith("go"):
            valid_moves = gs.get_valid_moves()
            best = ChessAI.find_best_move_nega_max(gs, valid_moves)
            if best is None:
                best = ChessAI.find_random_move(valid_moves)
            print(f"bestmove {best.getChessNotation()}")
            sys.stdout.flush()

        elif line == "quit":
            break


if __name__ == "__main__":
    uci_loop()