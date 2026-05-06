import random

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
                    score = -turn_multiplier * score_material(game_screen.board)
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

def min_max(game_screen, valid_moves, depth, white_to_move):
    global next_move
    if depth == 0:
        return score_board(game_screen.board)

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
    for row in game_screen.board:
        for square in row:
            if square[0] == 'w':
                score += piece_rank[square[1]]
            elif square[0] == 'b':
                score -= piece_rank[square[1]]
    return score
