import random

class TranspositionTable:
    EXACT = 0
    LOWERBOUND = 1
    UPPERBOUND = 2

    def __init__(self):
        self.table = {}

    def store(self, board_hash, depth, score, flag): #Overwrites if new entry is more valuable
        if board_hash not in self.table or self.table[board_hash][0] <= depth:
            self.table[board_hash] = (depth, score, flag)

    def lookup(self, board_hash, depth, alpha, beta):
        if board_hash not in self.table:
            return None
        stored_depth, score, flag = self.table[board_hash]
        if stored_depth >= depth:
            if flag == self.EXACT:
                return score
            elif flag == self.LOWERBOUND and score > alpha:
                alpha = score
            elif flag == self.UPPERBOUND and score < beta:
                beta = score
            if alpha >= beta:
                return score
        return None

transposition_table = TranspositionTable()

def hash_board(game_screen):
    return hash((tuple(tuple(row) for row in game_screen.board), game_screen.whiteToMove))


piece_rank = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1} #What score player gains when capturing following pieces
CHECKMATE = 1000 #Always best
STALEMATE = 0 #neither win nor lose
DEPTH=3
killer_moves = [[None, None] for _ in range(10)]


OPENING_BOOK = {
    # === FIRST MOVES ===
    "": ["e2e4", "d2d4"],

    # === AFTER 1.e4 ===
    "e2e4": ["e7e5", "c7c5", "e7e6", "c7c6", "d7d5"],

    # --- Italian Game / Ruy Lopez ---
    "e2e4e7e5": ["g1f3"],
    "e2e4e7e5g1f3": ["b8c6", "g8f6"],
    "e2e4e7e5g1f3b8c6": ["f1b5", "f1c4"],  # Ruy Lopez or Italian

    # Ruy Lopez main line
    "e2e4e7e5g1f3b8c6f1b5": ["a7a6", "g8f6", "f8c5"],
    "e2e4e7e5g1f3b8c6f1b5a7a6": ["b5a4"],
    "e2e4e7e5g1f3b8c6f1b5a7a6b5a4": ["g8f6"],
    "e2e4e7e5g1f3b8c6f1b5a7a6b5a4g8f6": ["e1g1"],  # Castle!
    "e2e4e7e5g1f3b8c6f1b5a7a6b5a4g8f6e1g1": ["f8e7", "b7b5"],

    # Italian Game
    "e2e4e7e5g1f3b8c6f1c4": ["f8c5", "g8f6", "e7e6"],
    "e2e4e7e5g1f3b8c6f1c4f8c5": ["c2c3", "e1g1"],
    "e2e4e7e5g1f3b8c6f1c4f8c5c2c3": ["g8f6", "d7d6"],
    "e2e4e7e5g1f3b8c6f1c4f8c5c2c3g8f6": ["d2d4"],

    # Petrov Defense
    "e2e4e7e5g1f3g8f6": ["f3e5", "d2d4"],
    "e2e4e7e5g1f3g8f6f3e5": ["d7d6", "f6e4"],

    # --- Sicilian Defense ---
    "e2e4c7c5": ["g1f3"],
    "e2e4c7c5g1f3": ["d7d6", "b8c6", "e7e6"],

    # Sicilian Najdorf
    "e2e4c7c5g1f3d7d6": ["d2d4"],
    "e2e4c7c5g1f3d7d6d2d4": ["c5d4"],
    "e2e4c7c5g1f3d7d6d2d4c5d4": ["f3d4"],
    "e2e4c7c5g1f3d7d6d2d4c5d4f3d4": ["g8f6"],
    "e2e4c7c5g1f3d7d6d2d4c5d4f3d4g8f6": ["b1c3"],
    "e2e4c7c5g1f3d7d6d2d4c5d4f3d4g8f6b1c3": ["a7a6"],  # Najdorf
    "e2e4c7c5g1f3d7d6d2d4c5d4f3d4g8f6b1c3a7a6": ["c1e3", "f2f3", "g2g4"],

    # Sicilian Dragon
    "e2e4c7c5g1f3b8c6": ["d2d4"],
    "e2e4c7c5g1f3b8c6d2d4": ["c5d4"],
    "e2e4c7c5g1f3b8c6d2d4c5d4": ["f3d4"],
    "e2e4c7c5g1f3b8c6d2d4c5d4f3d4": ["g7g6"],  # Dragon
    "e2e4c7c5g1f3b8c6d2d4c5d4f3d4g7g6": ["b1c3"],

    # Sicilian Scheveningen / Classical
    "e2e4c7c5g1f3e7e6": ["d2d4"],
    "e2e4c7c5g1f3e7e6d2d4": ["c5d4"],
    "e2e4c7c5g1f3e7e6d2d4c5d4": ["f3d4"],
    "e2e4c7c5g1f3e7e6d2d4c5d4f3d4": ["g8f6", "b8c6"],
    "e2e4c7c5g1f3e7e6d2d4c5d4f3d4g8f6": ["b1c3"],
    "e2e4c7c5g1f3e7e6d2d4c5d4f3d4g8f6b1c3": ["d7d6", "f8b4"],

    # --- French Defense ---
    "e2e4e7e6": ["d2d4"],
    "e2e4e7e6d2d4": ["d7d5"],
    "e2e4e7e6d2d4d7d5": ["b1c3", "e4e5", "e4d5"],
    "e2e4e7e6d2d4d7d5b1c3": ["g8f6", "f8b4"],  # Classical / Winawer
    "e2e4e7e6d2d4d7d5b1c3f8b4": ["e4e5", "a2a3"],  # Winawer
    "e2e4e7e6d2d4d7d5b1c3g8f6": ["c1g5"],  # Classical French

    # --- Caro-Kann ---
    "e2e4c7c6": ["d2d4"],
    "e2e4c7c6d2d4": ["d7d5"],
    "e2e4c7c6d2d4d7d5": ["b1c3", "e4d5", "e4e5"],
    "e2e4c7c6d2d4d7d5b1c3": ["d5e4", "g8f6"],
    "e2e4c7c6d2d4d7d5b1c3d5e4": ["c3e4"],
    "e2e4c7c6d2d4d7d5b1c3d5e4c3e4": ["g8f6", "c8f5"],

    # --- Scandinavian ---
    "e2e4d7d5": ["e4d5"],
    "e2e4d7d5e4d5": ["d8d5", "g8f6"],
    "e2e4d7d5e4d5d8d5": ["b1c3"],
    "e2e4d7d5e4d5d8d5b1c3": ["d5a5", "d5d6"],

    # === AFTER 1.d4 ===
    "d2d4": ["d7d5", "g8f6", "f7f5"],

    # --- Queen's Gambit ---
    "d2d4d7d5": ["c2c4"],
    "d2d4d7d5c2c4": ["e7e6", "c7c6", "d5c4"],

    # QGD
    "d2d4d7d5c2c4e7e6": ["b1c3", "g1f3"],
    "d2d4d7d5c2c4e7e6b1c3": ["g8f6", "f8e7"],
    "d2d4d7d5c2c4e7e6b1c3g8f6": ["c1g5", "g1f3"],
    "d2d4d7d5c2c4e7e6b1c3g8f6c1g5": ["f8e7", "b8d7"],
    "d2d4d7d5c2c4e7e6b1c3g8f6c1g5f8e7": ["e2e3", "g1f3"],

    # Slav Defense
    "d2d4d7d5c2c4c7c6": ["g1f3", "b1c3"],
    "d2d4d7d5c2c4c7c6g1f3": ["g8f6", "d5c4"],
    "d2d4d7d5c2c4c7c6g1f3g8f6": ["b1c3", "e2e3"],
    "d2d4d7d5c2c4c7c6g1f3g8f6b1c3": ["d5c4", "e7e6", "a7a6"],

    # QGA
    "d2d4d7d5c2c4d5c4": ["e2e4", "g1f3"],
    "d2d4d7d5c2c4d5c4e2e4": ["e7e5", "g8f6"],

    # --- King's Indian Defense ---
    "d2d4g8f6": ["c2c4"],
    "d2d4g8f6c2c4": ["g7g6", "e7e6", "c7c5"],
    "d2d4g8f6c2c4g7g6": ["b1c3", "g1f3"],
    "d2d4g8f6c2c4g7g6b1c3": ["f8g7"],
    "d2d4g8f6c2c4g7g6b1c3f8g7": ["e2e4"],  # KID main line
    "d2d4g8f6c2c4g7g6b1c3f8g7e2e4": ["d7d6", "e1g1"],
    "d2d4g8f6c2c4g7g6b1c3f8g7e2e4d7d6": ["g1f3"],
    "d2d4g8f6c2c4g7g6b1c3f8g7e2e4d7d6g1f3": ["e1g1"],
    "d2d4g8f6c2c4g7g6b1c3f8g7e2e4d7d6g1f3e1g1": ["e7e5"],  # KID Classical

    # --- Nimzo-Indian Defense ---
    "d2d4g8f6c2c4e7e6": ["b1c3"],
    "d2d4g8f6c2c4e7e6b1c3": ["f8b4"],  # Nimzo-Indian
    "d2d4g8f6c2c4e7e6b1c3f8b4": ["e2e3", "d1c2", "g1f3", "a2a3"],
    "d2d4g8f6c2c4e7e6b1c3f8b4e2e3": ["e1g1", "c7c5", "b7b6"],
    "d2d4g8f6c2c4e7e6b1c3f8b4d1c2": ["e1g1", "c7c5"],

    # --- Grünfeld Defense ---
    "d2d4g8f6c2c4g7g6b1c3": ["d7d5"],  # Grünfeld
    "d2d4g8f6c2c4g7g6b1c3d7d5": ["c4d5"],
    "d2d4g8f6c2c4g7g6b1c3d7d5c4d5": ["f6d5"],
    "d2d4g8f6c2c4g7g6b1c3d7d5c4d5f6d5": ["e2e4"],
    "d2d4g8f6c2c4g7g6b1c3d7d5c4d5f6d5e2e4": ["d5c3"],
    "d2d4g8f6c2c4g7g6b1c3d7d5c4d5f6d5e2e4d5c3": ["b2c3", "d1d8"],

    # --- Dutch Defense ---
    "d2d4f7f5": ["g2g3", "c2c4"],
    "d2d4f7f5c2c4": ["g8f6", "e7e6"],
    "d2d4f7f5c2c4g8f6": ["g2g3"],
    "d2d4f7f5c2c4g8f6g2g3": ["e7e6", "g7g6"],
}


def get_opening_moves(game_screen, valid_moves):
    moves_so_far = "".join(m.getChessNotation() for m in game_screen.move_log)
    if moves_so_far in OPENING_BOOK:
        candidates = OPENING_BOOK[moves_so_far]
        random.shuffle(candidates)
        for notation in candidates:
            for move in valid_moves:
                if move.getChessNotation() == notation:
                    return move
    return None

def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]

def find_best_move(game_screen, valid_moves):
    turn_multiplier = 1 if game_screen.whiteToMove else -1
    opponent_min_max_score = CHECKMATE
    best_player_move = None

    for player_move in valid_moves:
        game_screen.make_move(player_move)
        opponents_moves = game_screen.get_valid_moves()
        if game_screen.stalemate:
            opponents_max_score = STALEMATE
        elif game_screen.checkmate:
            opponents_max_score = -CHECKMATE
        else:
            opponents_max_score = -CHECKMATE
            for opponents_move in opponents_moves:
                game_screen.make_move(opponents_move)
                game_screen.get_valid_moves()
                if game_screen.checkmate:
                    score = CHECKMATE
                elif game_screen.stalemate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * score_board(game_screen.board)
                if score > opponents_max_score:
                    opponents_max_score = score
                game_screen.undo_move()
        if opponents_max_score < opponent_min_max_score:
            opponent_min_max_score = opponents_max_score
            best_player_move = player_move
        game_screen.undo_move()
    return best_player_move

def find_best_move_min_max(game_screen, valid_moves):
    global next_move
    next_move = None
    min_max(game_screen, valid_moves, DEPTH, game_screen.whiteToMove)
    return next_move

def quiescence(game_screen, alpha, beta, turn_multiplier):
    stand_pat = turn_multiplier * score_board(game_screen)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    captures = [move for move in game_screen.get_valid_moves() if move.pieceCaptured != "--"]
    captures = order_moves(captures)

    for move in captures:
        game_screen.make_move(move)
        score = -quiescence(game_screen, -beta, -alpha, -turn_multiplier)
        game_screen.undo_move()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha

def min_max(game_screen, valid_moves, depth, white_to_move):
    global next_move
    if depth == 0:
        return score_board(game_screen)

    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            game_screen.make_move(move)
            next_moves = game_screen.get_valid_moves()
            score = min_max(game_screen, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            game_screen.undo_move()
        return max_score
    else:
        min_score = CHECKMATE
        for move in valid_moves:
            game_screen.make_move(move)
            next_moves = game_screen.get_valid_moves()
            score = min_max(game_screen, next_moves, depth-1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            game_screen.undo_move()
        return min_score

def find_best_move_nega_max(game_screen, valid_moves):
    opening_move = get_opening_moves(game_screen, valid_moves)
    if opening_move:
        return opening_move

    global next_move
    best = None
    moves = list(valid_moves)

    for current_depth in range(1, DEPTH + 1):
        next_move = None
        nega_max_alpha_beta_pruning(game_screen, moves, current_depth,
                                    -CHECKMATE, CHECKMATE,
                                    1 if game_screen.whiteToMove else -1)
        if next_move:
            best = next_move
            if best in moves:
                moves.remove(best)
                moves.insert(0, best)

    return best

def nega_max_alpha_beta_pruning(game_screen, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move

    board_hash = hash_board(game_screen)
    table_result = transposition_table.lookup(board_hash, depth, alpha, beta)
    if table_result is not None:
        return table_result

    if depth == 0:
        return quiescence(game_screen, alpha, beta, turn_multiplier)

    # Null move pruning
    R = 2
    if depth >= 3 and not game_screen.inCheck:
        game_screen.whiteToMove = not game_screen.whiteToMove
        null_score = -nega_max_alpha_beta_pruning(game_screen,
                      game_screen.get_valid_moves(), depth - 1 - R,
                      -beta, -beta + 1, -turn_multiplier)
        game_screen.whiteToMove = not game_screen.whiteToMove
        if null_score >= beta:
            return beta

    valid_moves = order_moves(valid_moves, depth)

    original_alpha = alpha
    max_score = -CHECKMATE

    for move in valid_moves:
        game_screen.make_move(move)
        next_moves = game_screen.get_valid_moves()
        score = -nega_max_alpha_beta_pruning(game_screen, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        game_screen.undo_move()

        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move

        if max_score > alpha:
            alpha = max_score

        if alpha >= beta:
            if move.pieceCaptured == "--":
                store_killer(move, depth)
            break

    if max_score <= original_alpha:
        flag = TranspositionTable.UPPERBOUND
    elif max_score >= beta:
        flag = TranspositionTable.LOWERBOUND
    else:
        flag = TranspositionTable.EXACT
    transposition_table.store(board_hash, depth, max_score, flag)

    return max_score

def store_killer(move, depth):
    if killer_moves[depth][0] != move:
        killer_moves[depth][1] = killer_moves[depth][0]
        killer_moves[depth][0] = move

def score_move(move, depth=0):
    if move.pieceCaptured != "--":
        return 10000 + 10 * piece_rank[move.pieceCaptured[1]] - piece_rank[move.piece_moved[1]]
    if depth < len(killer_moves):
        if move == killer_moves[depth][0]:
            return 9000
        if move == killer_moves[depth][1]:
            return 8000
    return 0

def order_moves(moves, depth=0):
    return sorted(moves, key=lambda m: score_move(m, depth), reverse=True)

knight_table = [
    [-5, -4, -3, -3, -3, -3, -4, -5],
    [-4, -2,  0,  0,  0,  0, -2, -4],
    [-3,  0,  1,  2,  2,  1,  0, -3],
    [-3,  1,  2,  3,  3,  2,  1, -3],
    [-3,  0,  2,  3,  3,  2,  0, -3],
    [-3,  1,  1,  2,  2,  1,  1, -3],
    [-4, -2,  0,  1,  1,  0, -2, -4],
    [-5, -4, -3, -3, -3, -3, -4, -5]
]

pawn_table = [
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 5,  5,  5,  5,  5,  5,  5,  5],
    [ 1,  1,  2,  3,  3,  2,  1,  1],
    [ 0,  0,  1,  2,  2,  1,  0,  0],
    [ 0,  0,  0,  2,  2,  0,  0,  0],
    [ 0, -1, -1,  0,  0, -1, -1,  0],
    [ 0,  1,  1, -2, -2,  1,  1,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0]
]

bishop_table = [
    [-2,-1,-1,-1,-1,-1,-1,-2],
    [-1, 0, 0, 0, 0, 0, 0,-1],
    [-1, 0, 1, 1, 1, 1, 0,-1],
    [-1, 1, 1, 2, 2, 1, 1,-1],
    [-1, 0, 2, 2, 2, 2, 0,-1],
    [-1, 2, 2, 2, 2, 2, 2,-1],
    [-1, 1, 0, 0, 0, 0, 1,-1],
    [-2,-1,-1,-1,-1,-1,-1,-2]
]

rook_table = [
    [ 0, 0, 0, 0, 0, 0, 0, 0],
    [ 1, 2, 2, 2, 2, 2, 2, 1],
    [-1, 0, 0, 0, 0, 0, 0,-1],
    [-1, 0, 0, 0, 0, 0, 0,-1],
    [-1, 0, 0, 0, 0, 0, 0,-1],
    [-1, 0, 0, 0, 0, 0, 0,-1],
    [-1, 0, 0, 0, 0, 0, 0,-1],
    [ 0, 0, 0, 1, 1, 0, 0, 0]
]

king_table = [
    [-3,-4,-4,-5,-5,-4,-4,-3],
    [-3,-4,-4,-5,-5,-4,-4,-3],
    [-3,-4,-4,-5,-5,-4,-4,-3],
    [-3,-4,-4,-5,-5,-4,-4,-3],
    [-2,-3,-3,-4,-4,-3,-3,-2],
    [-1,-2,-2,-2,-2,-2,-2,-1],
    [ 2, 2, 0, 0, 0, 0, 2, 2],
    [ 2, 3, 1, 0, 0, 1, 3, 2]
]

position_tables = {'N': knight_table, 'p': pawn_table, 'B': bishop_table, 'R': rook_table, 'K': king_table}
#Positive good for white, negative good for black
def score_board(game_screen):
    if game_screen.checkmate:
        if game_screen.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif game_screen.stalemate:
        return STALEMATE

    score = 0
    for row in range(8):
        for column in range(8):
            square = game_screen.board[row][column]
            if square[0] == 'w':
                score += piece_rank[square[1]]
                if square[1] in position_tables:
                    score += position_tables[square[1]][row][column] * 0.1
            elif square[0] == 'b':
                score -= piece_rank[square[1]]
                if square[1] in position_tables:
                    score -= position_tables[square[1]][7 - row][column] * 0.1
    return score
