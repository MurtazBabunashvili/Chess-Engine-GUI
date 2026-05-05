import random

piece_rank = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1} #What score player gains when capturing following pieces
CHECKMATE = 1000 #Always best
STALEMATE = 0 #neither win nor lose

def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]

def find_best_move(game_screen, valid_moves):
    turn_multiplier = 1 if game_screen.whiteToMove else -1
    opponent_min_max_score = CHECKMATE
    best_player_move = None

    for player_move in valid_moves:
        opponents_max_score = -CHECKMATE
        game_screen.make_move(player_move)
        opponents_moves = game_screen.get_valid_moves()
        for opponents_move in opponents_moves:
            game_screen.make_move(opponents_move)
            if game_screen.checkmate:
                score = CHECKMATE
            elif game_screen.stalemate:
                score = STALEMATE
            else:
                score = -turn_multiplier * score_material(game_screen.board)
            if score > opponents_max_score:
                opponents_max_score = score
            game_screen.undo_move()
        if opponents_max_score < opponent_min_max_score:
            opponent_min_max_score = opponents_max_score
            best_player_move = player_move
        game_screen.undo_move()
    return best_player_move


def score_material(board): #Calculates score given current board
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piece_rank[square[1]]
            elif square[0] == 'b':
                score -= piece_rank[square[1]]
    return score
