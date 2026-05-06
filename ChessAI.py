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
DEPTH=4

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
    global next_move
    next_move = None
    nega_max_alpha_beta_pruning(game_screen, valid_moves, DEPTH,-CHECKMATE, CHECKMATE, 1 if game_screen.whiteToMove else -1)
    return next_move

def nega_max_alpha_beta_pruning(game_screen, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move

    board_hash = hash_board(game_screen)
    table_result = transposition_table.lookup(board_hash, depth, alpha, beta)

    if table_result is not None:
        return table_result

    if depth == 0:
        return quiescence(game_screen, alpha, beta, turn_multiplier)

    #Move ordering
    valid_moves = order_moves(valid_moves)

    original_alpha = alpha
    max_score = -CHECKMATE
    for move in valid_moves:
        game_screen.make_move(move)
        next_moves = game_screen.get_valid_moves()
        score = -nega_max_alpha_beta_pruning(game_screen, next_moves, depth-1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        game_screen.undo_move()
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break

    if max_score <= original_alpha:
        flag = TranspositionTable.UPPERBOUND
    elif max_score >= beta:
        flag = TranspositionTable.LOWERBOUND
    else:
        flag = TranspositionTable.EXACT
    transposition_table.store(board_hash, depth, max_score, flag)

    return max_score

def score_move(move):
    score =0
    if move.pieceCaptured != "--":
        #If we capture queen with pawn = great, if pawn with queen => less urgent
        score = 10 * piece_rank[move.pieceCaptured[1]] - piece_rank[move.piece_moved[1]]
    return score
def order_moves(moves):
    return sorted(moves, key=score_move, reverse=True)

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

position_tables = {'N': knight_table, 'p': pawn_table}
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
